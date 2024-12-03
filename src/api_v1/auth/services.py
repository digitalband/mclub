import json
import secrets
import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.utils import JWTHandler
from api_v1.auth.schemas import SignUpSchema, PayloadSchema, TokenPairSchema, \
                                        VerificationCodeSchema, SignInSchema
from api_v1.auth.repositories.user import UserRepository
from api_v1.exceptions import EmailAlreadyExistsException, EmailNotFoundException, \
                    VerificationCodeIncorrectException, UserNotCreatedException
from api_v1.email.services import EmailService
from api_v1.email.schemas import MessageSchema, MessageType
from core.config import settings
from core.redis.redis_helper import redis_helper

log = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self, 
        private_key: str,
        public_key: str,
        algorithm: str,
        verification_code_length: int,
        session: AsyncSession
    ) -> None:
        self.jwt_handler = JWTHandler(
            private_key=private_key,
            public_key=public_key,
            algorithm=algorithm,
        )
        self.email_service = EmailService(
            smtp_host=settings.email.SMTP_HOST,
            smtp_port=settings.email.SMTP_PORT,
            smtp_user=settings.email.SMTP_USER,
            smtp_password=settings.email.SMTP_PASS
        )
        self.verification_code_length = verification_code_length
        self.user_repo = UserRepository(session=session)


    async def signup(self, signup_data: SignUpSchema) -> bool:
        """
        Generating a verification code, and sending it to the user's email.

        Args:
            signup_data (SignUpSchema): The data required for user registration

        Returns:
            bool: True if the registration process is successful and 
            the verification code is sent; otherwise, an exception is raised.
        """
        if not await self.check_email_availability(signup_data.email):
            raise EmailAlreadyExistsException
        
        verification_code = await self.__create_verification_code(
            email=signup_data.email,
            signup_data=signup_data
        )

        if not verification_code:
            raise ValueError("Verification code not created")
        
        email_status = await self.__send_verification_code(
            email=signup_data.email,
            verification_code=verification_code,
        )
        if not email_status:
            raise ValueError("Email don't send")

        return True
    
    async def signin(self, signin_data: SignInSchema) -> bool:
        """
        Generating a verification code, and sending it to the user's email.

        Args:
            signin_data (SignInSchema): The data required for user auth

        Returns:
            bool: True if the registration process is successful and 
            the verification code is sent; otherwise, an exception is raised.
        """
        if await self.check_email_availability(signin_data.email):
            raise EmailNotFoundException

        verification_code = await self.__create_verification_code(
            email=signin_data.email
        )

        if not verification_code:
            raise ValueError("Verification code not created")
        
        email_status = await self.__send_verification_code(
            email=signin_data.email,
            verification_code=verification_code,
        )
        if not email_status:
            raise ValueError("Email don't send")

        return True

    async def __create_verification_code(
        self, email: str, *, signup_data: Optional[SignUpSchema] = None
    ) -> str | None:
        """
        Generates a verification code for the given email and stores it in Redis
        
        Args:
            email (str): The email address to which the verification code will be sent.
            signup_data (Optional[SignUpSchema]): An optional schema containing 
            additional signup information. If provided, this data will be included 
            in the stored value alongside the verification code.
            
        Returns:
            str | None: Returns the generated verification code as a string if the 
            вcode was successfully added to Redis; otherwise, returns None.
        """
        verification_code = ''.join(
            secrets.choice("0123456789")
            for _ in range(self.verification_code_length)
        )

        value = {
            "verification_code": verification_code,
        }

        if signup_data:
            value["signup_data"] = signup_data.model_dump()
        
        add_code_in_redis_status = await redis_helper.add_verification_code(
                email=email,
                value=json.dumps(value),
                expiration=settings.auth_jwt.verification_code_expiration_minutes,
            )

        if not add_code_in_redis_status:
            return None
        
        return verification_code

    async def __send_verification_code(self, email: str, verification_code: str) -> bool:
        """
        Sends a confirmation code to the specified email
       
        Args:
            email (str): The recipient's email address.
            verification_code (str): confirmation code that will be sent by email
        
        Returns:
            bool: True if the message was send successfully / False if the message is not delivery
        """
        message = MessageSchema(
            message_type=MessageType.verification_code,
            message=verification_code
        )

        email_status = await self.email_service.send_message(
            recipient=email,
            message=message
        )

        return email_status

    async def verify_code(
        self, verification_data: VerificationCodeSchema
    ) -> TokenPairSchema:
        """
        Verifying the confirmation code.
        
        Args:
            verification_data (VerificationCodeSchema): email and verification_code

        Returns:
            TokenPairSchema: An object containing the generated
                             access and refresh tokens.
        """
        data = await redis_helper.get_verification_code(email=verification_data.email)
        
        if not data:
            raise VerificationCodeIncorrectException
        
        data = json.loads(data)

        if data["verification_code"] != verification_data.verification_code:
            raise VerificationCodeIncorrectException
        
        if signup_data := data.get("signup_data", None):
            user_created = await self.create_user(signup_data)
            if not user_created:
                raise UserNotCreatedException
    
        payload = await self.get_user_payload(verification_data.email)
        
        return self.__generate_auth_token_pair(payload) # TODO: add async

    async def create_user(self, signup_data: SignUpSchema) -> bool:
        pass

    async def get_user_payload(self, email: str) -> PayloadSchema:
        pass

    async def check_email_availability(self, email: str) -> bool:
        """
        Args:
            email (str): email for checking

        Returns:
            bool: True if email available / False is email is busy
        """
        user = await self.user_repo.get_user_by_email(email)
        return user is None
    
    def __generate_auth_token_pair(self, payload: PayloadSchema) -> TokenPairSchema:
        """
        Generates a pair of tokens (access and refresh)

        Args:
            payload (PayloadSchema): An object containing the data for
                                     token generation.

        Returns:
            TokenPairSchema: An object containing the generated
                             access and refresh tokens.
        """
        payload_data = payload.model_dump()

        access_token = self.__generate_auth_token(payload_data, is_refresh=False)
        refresh_token = self.__generate_auth_token(payload_data, is_refresh=True)

        return TokenPairSchema(access_token=access_token, refresh_token=refresh_token)

    def __generate_auth_token(
        self, payload_data: dict[str, Any], is_refresh: bool
    ) -> str:
        """
        Generates a JWT token based on the provided payload data.

        Args:
            payload_data (dict[str, Any]): A dictionary containing the data
                                           to be encoded in the token.
            is_refresh (bool): A flag indicating whether the token being
                               generated is a refresh token.

        Returns:
            str: The encoded JWT token as a string.
        """
        payload_data["is_refresh"] = is_refresh

        if is_refresh:
            expire_minutes = settings.auth_jwt.refresh_token_expire_minutes
        else:
            expire_minutes = settings.auth_jwt.access_token_expire_minutes

        return self.jwt_handler.encode(
            payload=payload_data, expire_token=expire_minutes
        )