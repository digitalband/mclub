import logging

from fastapi import APIRouter, HTTPException, status

from api_v1.auth.schemas import *
from api_v1.auth.dependencies import AuthDependency
from api_v1.exceptions import APIException


router = APIRouter()
log = logging.getLogger(__name__)


@router.post(
    path="/check_email",
    response_model=EmailAvailabilityResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Checking email availability",
    response_description="Email availability status"
)
async def check_email(
    email: CheckEmailSchema,
    auth_service: AuthDependency
) -> EmailAvailabilityResponseSchema:
    """
    Endpoint to checking email availability

    This endpoint checks whether the specified email is available for registration

    Args:
	    email: (EmailStr) Email for checking

    Returns:
	    EmailAvailabilityResponseSchema: Returns a JSON response with the email 
                                         availability status
    """
    try:
        email_exists = await auth_service.check_email_availability(email.email)
        return EmailAvailabilityResponseSchema(email_avaibility=email_exists)
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        logging.error(f"Failed check email > {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed check email"
        )


@router.post(
    path="/signup",
    response_model=SignInResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Registration",
    response_description="Returns registration confirmation status."
    )
async def signup(
    signup_data: SignUpSchema,
    auth_service: AuthDependency
) -> SignInResponseSchema:
    """
    Endpoint for registering a new user.
    
    This endpoint allows new users to provide the necessary registration information. 
    If the data is correct, a confirmation code is sent to the specified email address
    to confirm registration.
    
    Args:
        signup_data (SignUpSchema): Data required to register a new user,
                                    including fields such as email, first name, 
                                    last name and phone number (optional field).

    Returns:
        SignInResponseSchema: Returns a JSON response indicating that 
                              the verification code was successfully sent 
                              to the email.
    """
    try:
        await auth_service.register_user(signup_data)
        return SignInResponseSchema(status="OK")
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        logging.error(f"Failed signup > {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed signup"
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

    Args:
        verification_data (VerificationCodeSchema): Email user code from 
                                                    the message sent by email

    Returns:
        TokenPairSchema: Returns a JSON response with access and refresh tokens
    """
    try:
        token_pair = await auth_service.verify_code(verification_data)
        return token_pair
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        logging.error(f"Failed verification code > {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed verification code"
        )
