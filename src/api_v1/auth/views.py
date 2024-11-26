import logging

from fastapi import APIRouter, HTTPException, status, Depends

from api_v1.auth.schemas import SignUpSchema, SignUpResponseSchema
from api_v1.auth.services import AuthService
from api_v1.auth.dependencies import auth_service_depends
from api_v1.exceptions.api_exceptions import APIException


router = APIRouter()
log = logging.getLogger(__name__)


@router.post(
    path="/signup",
    response_model=SignUpResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="Return the user ID for the created user"
    )
async def signup(
    signup_data: SignUpSchema,
    auth_service: AuthService = Depends(auth_service_depends)
) -> SignUpResponseSchema:
    """
    Endpoint to register a new user.

    This endpoint allows new users to sign up by providing the necessary
    information. If the registration is successful, it returns the user ID
    of the newly created user.
    
    Args:
        signup_data (SignUpSchema): The data required to register a new user,
                                    including fields such as email, first name, 
                                    last name, and optional phone number.

    Returns:
        SignUpResponseSchema: Returns a JSON response with the user ID
    """
    try:
        user_id = await auth_service.register_user(signup_data)
        return SignUpResponseSchema(user_id=user_id)
    except APIException as api_exception:
        raise api_exception
    except Exception as e:
        logging.error(f"Failed signup > {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed signup"
        )
