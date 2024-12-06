import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr

from schemas.auth import *
from dependencies.auth import AuthDependency
from exceptions.api_exceptions import APIException


router = APIRouter()
log = logging.getLogger(__name__)


@router.get(
    path="/check_email",
    response_model=EmailAvailabilityResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Checking email availability",
    response_description="Email availability status"
)
async def check_email(
    email: EmailStr,
    auth_service: AuthDependency
) -> EmailAvailabilityResponseSchema:
    """Endpoint to checking email availability"""
    try:
        email_exists = await auth_service.check_email_availability(email)
        return EmailAvailabilityResponseSchema(email_avaibility=email_exists)
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        log.error("Failed check email > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed check email"
        )


@router.post(
    path="/signup",
    response_model=SignUpResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Registration",
    response_description="Returns registration confirmation status."
    )
async def signup(
    signup_data: SignUpSchema,
    auth_service: AuthDependency
) -> SignUpResponseSchema:
    """
    Endpoint for registering a new user.
    
    This endpoint allows new users to provide the necessary registration information. 
    If the data is correct, a confirmation code is sent to the specified email address
    to confirm registration.
    """
    try:
        await auth_service.signup(signup_data)
        return SignInResponseSchema(status="OK")
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        log.error("Failed signup > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed signup"
        )
    

@router.post(
    path="/signin",
    response_model=SignInResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Login",
    response_description="Returns login confirmation status."
)
async def signin(
    signin_data: SignInSchema,
    auth_service: AuthDependency
) -> SignInResponseSchema:
    """
    Endpoint for login user.
    
    This endpoint allows users to provide the necessary login information. 
    If the data is correct, a confirmation code is sent to the specified email 
    address to confirm registration.
    """
    try:
        await auth_service.signin(signin_data)
        return SignInResponseSchema(status="OK")
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        log.error("Failed signin > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed signin"
        )


@router.post(
    path="/verify-code",
    response_model=TokenPairSchema,
    status_code=status.HTTP_200_OK,
    summary="Verifying the confirmation code",
    response_description="Return access and refresh tokens"
)
async def verify_code(
    verification_data: VerificationCodeSchema,
    auth_service: AuthDependency
) -> TokenPairSchema:
    """
    Endpoint to verifying the confirmation code.
    
    This endpoint allows users to enter a confirmation code, sent to their email.
    """
    try:
        token_pair = await auth_service.verify_code(verification_data)
        return token_pair
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        log.error("Failed verification code > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed verification code"
        )


@router.post(
    path="/validate",
    response_model=PayloadSchema,
    status_code=status.HTTP_200_OK,
    summary="Validate access token",
    response_description="Payload from token"
)
async def validate_token(
    token: AccessTokenSchema,
    auth_service: AuthDependency
) -> PayloadSchema:
    """Endpoint to validate access token"""
    try:
        payload = await auth_service.validate_token(token.access_token)
        return payload
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        log.error("Failed validate token > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed validation token"
        )


@router.post(
    path="/refresh",
    response_model=TokenPairSchema,
    status_code=status.HTTP_200_OK,
    summary="Token pair update",
    response_description="Return updated access and refresh tokens"
)
async def refresh_token(
    token: RefreshTokenSchema,
    auth_service: AuthDependency
) -> TokenPairSchema:
    """Endpoint to refresh token pair"""
    try:
        token_pair = await auth_service.refresh_token(token.refresh_token)
        return token_pair
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        log.error("Failed refresh token > %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed refresh token"
        )
    

@router.post(
    path="/signout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Signout from account"
    )
async def signout() -> None:
    pass