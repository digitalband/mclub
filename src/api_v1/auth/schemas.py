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


class SignUpSchema(BaseModel):
    email: EmailStr
    first_name: Annotated[str, Field(max_length=50)]
    last_name: Annotated[str, Field(max_length=50)]
    phone: Optional[PhoneNumber] = None


class SignUpResponseSchema(BaseModel):
    user_id: str
