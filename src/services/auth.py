import uuid
import json
import logging
import secrets
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING, Optional, Any


from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from core.config import settings
from core.redis.redis_helper import redis_helper
from utils.auth import JWTHandler
from schemas.auth import *
from schemas.email import MessageSchema, MessageType
from services.user import UserService
from services.email import EmailService
from services.session import SessionService
from exceptions.api_exceptions import *

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
        self.user_service = UserService(session=session)
        self.session_service = SessionService(session=session)
        self.verification_code_length = verification_code_length

    async def check_email_availability(self, email: str) -> bool:
        user = await self.user_service.get_user_by_email(email)
        return user is None
    
    async def signup(self, signup_data: SignUpSchema) -> bool:
        """
        Generating a verification code, and sending it to the user's email.

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

        Returns:
            str | None: Returns the generated verification code as a string if the 
            code was successfully added to Redis; otherwise, returns None.
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
                expiration=settings.auth_jwt.verification_code_expiration_seconds,
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
    
    async def verify_code(self, verification_data: VerificationCodeSchema) -> TokenPairSchema:
        """Verifying the confirmation code"""
        data = await redis_helper.get_verification_code(email=verification_data.email)
        
        if data is None:
            raise VerificationCodeIncorrectException
        
        data = json.loads(data)

        if data["verification_code"] != verification_data.verification_code:
            raise VerificationCodeIncorrectException
        
        if signup_data := data.get("signup_data", None):
            signup_schema = SignUpSchema(**signup_data) 
            user_created = await self.user_service.create_user(signup_schema)
            if user_created is None:
                raise UserNotCreatedException
    
        token_pair = await self.__open_auth_session(verification_data.email)

        await redis_helper.delete_verification_code(email=verification_data.email)

        return token_pair
    
    async def __open_auth_session(self, email: str) -> TokenPairSchema:
        """Created new session for user"""
        session_id = str(uuid.uuid4())
        user = await self.user_service.get_user_by_email(email)
        
        if user is None:
            raise EmailNotFoundException
        
        if not user.is_active:
            raise EmailNotFoundException

        payload = PayloadSchema(
            sub=str(user.id),
            jid=session_id,
            role=user.role,
        )

        token_pair = self.__generate_auth_token_pair(payload) # TODO: add async

        await self.session_service.create_session(
            user_id=user.id,
            session_id=session_id,
            refresh_token=token_pair.refresh_token,
            expires_at=datetime.now(timezone.utc)+timedelta(minutes=settings.auth_jwt.refresh_token_expire_minutes)
        )

        return token_pair
    
    def __generate_auth_token_pair(self, payload: PayloadSchema) -> TokenPairSchema:
        """Generates a pair of tokens (access and refresh)"""
        payload_data = payload.model_dump()

        access_token = self.__generate_auth_token(payload_data, is_refresh=False)
        refresh_token = self.__generate_auth_token(payload_data, is_refresh=True)

        return TokenPairSchema(access_token=access_token, refresh_token=refresh_token)

    def __generate_auth_token(self, payload_data: dict[str, Any], is_refresh: bool) -> str:
        """Generates a JWT token based on the provided payload data."""
        payload_data["is_refresh"] = is_refresh

        if is_refresh:
            expire_minutes = settings.auth_jwt.refresh_token_expire_minutes
        else:
            expire_minutes = settings.auth_jwt.access_token_expire_minutes

        return self.jwt_handler.encode(
            payload=payload_data, expire_token=expire_minutes
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenPairSchema:
        """Generate new token pair (access and refresh) tokens"""
        payload = await self.validate_token(refresh_token, is_refresh=True)
        user = await self.user_service.get_user_by_id(int(payload.sub))
        
        if not user.is_active:
            raise InvalidTokenException

        session = await self.session_service.get_session_by_id(payload.jid)

        if session is None:
            raise InvalidTokenException
        
        if refresh_token != session.refresh_token:
            raise InvalidTokenException

        payload.role = user.role
        token_pair = self.__generate_auth_token_pair(payload)

        await self.session_service.update_session(
            session=session,
            refresh_token=token_pair.refresh_token,
            expires_at=datetime.now(timezone.utc)+timedelta(minutes=settings.auth_jwt.refresh_token_expire_minutes)
        )

        return token_pair
    
    async def validate_token(self, token: str, is_refresh: bool = False) -> PayloadSchema:
        """
        Validates the provided jwt token.

        This method checks the token's payload, verifies if it is a refresh token 
        (if applicable), and checks if the token is in a blacklist.
        """
        payload = self.get_payload_from_token(token) # TODO: add async
        print(payload)
        if payload.is_refresh != is_refresh:
            raise InvalidTokenException

        if await redis_helper.session_in_black_list(payload.jid):
            raise InvalidTokenException

        return payload
    
    def get_payload_from_token(self, token: str) -> PayloadSchema:
        """Decodes the provided JWT and extracts the payload."""
        try:
            payload_dict = self.jwt_handler.decode(token=token) # TODO: add async
            payload = PayloadSchema(**payload_dict)
            return payload
        except ExpiredSignatureError:
            raise TokenExpiredException
        except InvalidTokenError:
            raise InvalidTokenException
        
    async def signout(self, session_id: str) -> bool:
        if await self.session_service.delete_session(session_id):
            return await redis_helper.add_session_in_black_list(session_id, settings.auth_jwt.access_token_expire_minutes*60)
        
        return False