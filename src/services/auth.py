import uuid
import json
import logging
import secrets
from datetime import datetime, timezone, timedelta
from typing import Any


from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from core.config import settings
from core.redis.redis_helper import redis_helper
from utils.auth import JWTHandler, PasswordHandler
from schemas.auth import *
from schemas.email import MessageSchema, MessageType
from services.user import UserService
from services.email import EmailService
from services.session import SessionService
from exceptions.api_exceptions import *
from models.user import User

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

    async def signin_with_password(self, signin_data: SignInWithPasswordSchema) -> TokenPairSchema:
        user = await self.user_service.get_user_by_email(signin_data.email)
        
        if not user or not PasswordHandler.validate(signin_data.password, user.hashed_password):
            raise UnauthorizedUserException
        
        token_pair = await self.__open_auth_session(user)
        return token_pair
        
    async def auth_request(self, request_data: SignUpSchema | SignInSchema) -> bool:
        """Generating a verification code, and sending it to the user's email."""
        if not await self.user_service.check_email_availability(request_data.email):
            raise EmailAlreadyExistsException

        verification_code = await self.__create_verification_code(request_data)

        if not verification_code:
            raise ValueError("Verification code not created")
        
        email_status = await self.__send_verification_code(
            email=request_data.email,
            verification_code=verification_code,
        )
        return email_status
    
    async def __create_verification_code(self, request_data:  SignUpSchema | SignInSchema) -> str | None:
        """Generates a verification code for the given email and stores it in Redis"""
        verification_code = ''.join(
            secrets.choice("0123456789")
            for _ in range(self.verification_code_length)
        )

        value = {"verification_code": verification_code}

        if isinstance(request_data, SignUpSchema):
            value["signup_data"] = request_data.model_dump()
        
        if await redis_helper.add_verification_code(
                email=request_data.email,
                value=json.dumps(value),
                expiration=settings.auth_jwt.verification_code_expiration_seconds,
        ):
            return verification_code
    
    async def __send_verification_code(self, email: str, verification_code: str) -> bool:
        """Sends a confirmation code to the specified email"""
        message = MessageSchema(
            message_type=MessageType.verification_code,
            message=verification_code
        )

        email_status = await self.email_service.send_message(
            recipient=email,
            message=message
        )

        return email_status
    
    async def check_verification_code(self, verification_data: VerificationCodeSchema) -> TokenPairSchema:
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
    
        user = await self.user_service.get_user_by_email(verification_data)
        
        if not user or not user.is_active:
            raise EmailNotFoundException

        token_pair = await self.__open_auth_session(user)

        await redis_helper.delete_verification_code(email=verification_data.email)

        return token_pair
    
    async def __open_auth_session(self, user: User) -> TokenPairSchema:
        """Created new session for user"""
        session_id = str(uuid.uuid4())

        payload = PayloadSchema(
            sub=str(user.id),
            jid=session_id,
            role=user.role,
        )

        token_pair = self.__generate_auth_token_pair(payload) # TODO: add async
        
        auth_session = SessionSchema(
            user_id=user.id,
            session_id=session_id,
            refresh_token=token_pair.refresh_token,
            expires_at=datetime.now(timezone.utc)+timedelta(minutes=settings.auth_jwt.refresh_token_expire_minutes)
        )
        await self.session_service.create_session(auth_session)

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
        
        if not user or not user.is_active:
            raise InvalidTokenException

        session = await self.session_service.get_session_by_id(payload.jid)

        if not session or refresh_token != session.refresh_token:
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