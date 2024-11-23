from typing import Any, Optional, Union
from datetime import datetime, timezone, timedelta

import jwt
import bcrypt


class JWTHandler:
    def __init__(
        self,
        private_key: str,
        public_key: str,
        algorithm: str
    ) -> None:
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm

    def encode(
        self, 
        payload: dict[str, Any],
        expire_token: Union[int, timedelta]
    ) -> str:
        """
        Encodes data into a JWT token

        Args:
            payload (dict[str, Any]): A dictionary with the data to be encoded
                                      into the token.    
            expire_token (Union[int, timedelta]): The time for the token to 
                expire. Can be specified in minutes (int) or as timedelta.

        Returns:
            str: JWT encoded token
        """
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)

        if isinstance(expire_token, int):
            expire = now+timedelta(minutes=expire_token)
        elif isinstance(expire_token, timedelta):
            expire = now + expire_token
        else:
            raise ValueError("expire_token must be an int or timedelta")
        
        to_encode.update(
            exp=expire,
            iat=now
        )
        return jwt.encode(
            payload=to_encode,
            key=self.private_key,
            algorithm=self.algorithm
        )

    def decode(self, token: str) -> dict[str, Any]:
        """
        Decodes a JWT token and returns the payload.

        Args:
            token (str): The JWT token to be decoded.

        Returns:
            dict[str, Any]: The decoded payload as a dictionary.
        """
        return jwt.decode(
            jwt=token,
            key=self.public_key,
            algorithms=self.algorithm
        )


class PasswordHandler:
    @staticmethod
    def hash(password: str, rounds: int = 12) -> bytes:
        """
        Hash a plain text password.
      
        Args:
            password (str): The plain text password to be hashed.
            rounds (int, optional): The number of hashing rounds. Default is 12.
                Increasing the number of rounds makes the hashing process 
                slower, which enhances security by making brute-force attacks 
                more difficult. More rounds mean that it takes longer to 
                compute the hash, thus increasing the time required for an 
                attacker to guess the password through repeated attempts. 
                It is recommended to choose a value between 10 and 14, 
                depending on the security requirements and performance 
                considerations.

        Returns:
            bytes: The hashed password as a byte string.
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds))

    @staticmethod
    def validate(password: str, hashed_password: bytes) -> bool:
        """
        Validate a plain text password against a hashed password.

        Args:
            password (str): The plain text password to validate.
            hashed_password (bytes): The hashed password to compare against.

        Returns:
            bool: True if the password matches the hashed password, 
                  False otherwise.
        """
        return bcrypt.checkpw(
            password=password.encode(),
            hashed_password=hashed_password
        )