from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MessageType(Enum):
    verification_code: str = "verification-code"


class Message(BaseModel):
    message_type: MessageType
    message: Optional[str]  = None
    link: Optional[str] = None
