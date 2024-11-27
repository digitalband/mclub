from typing import Annotated, Optional

from pydantic import BaseModel, Field, EmailStr

from pydantic_extra_types.phone_numbers import PhoneNumber


class PayloadSchema(BaseModel):
    sub: str
    role: Annotated[str, Field(max_length=8)]
    session_id: str
    is_refresh: bool = False


class TokenPairSchema(BaseModel):
    access_token: str
    refresh_token: str


class CheckEmailSchema(BaseModel):
    email: EmailStr


class SignUpSchema(BaseModel):
    email: EmailStr
    first_name: Annotated[str, Field(max_length=50)]
    last_name: Annotated[str, Field(max_length=50)]
    phone: Optional[PhoneNumber] = None


class BaseResponseSchema(BaseModel):
    status: str


class SignInResponseSchema(BaseResponseSchema):
    pass


class VerificationCodeSchema(BaseModel):
    email: EmailStr
    verification_code: int


class EmailAvailabilityResponseSchema(BaseModel):
    email_avaibility: bool