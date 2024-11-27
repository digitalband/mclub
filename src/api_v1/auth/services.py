from typing import Any

from api_v1.auth.utils import JWTHandler
from api_v1.auth.schemas import SignUpSchema, PayloadSchema, TokenPairSchema, \
                                    VerificationCodeSchema
from api_v1.exceptions import UserAlreadyExistsException
from core.config import settings


class AuthService:
    def __init__(self, private_key: str, public_key: str, algorithm: str) -> None:
        self.jwt_handler = JWTHandler(
            private_key=private_key,
            public_key=public_key,
            algorithm=algorithm,
        )
        self.user_service = UserService()


    async def register_user(self, signup_data: SignUpSchema) -> bool:
        pass

    async def verify_code(
        self, verification_data: VerificationCodeSchema
    ) -> TokenPairSchema:
        pass

    async def check_email_availability(self, email: str) -> bool:
        user = await self.user_service.get_user_by_email(email)
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


class UserService:
    def __init__(self) -> None:
        pass