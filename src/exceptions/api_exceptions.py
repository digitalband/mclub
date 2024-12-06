from fastapi import status


class APIException(Exception):
    status_code = None
    detail = None

    def __str__(self):
        return f"{self.detail}"


class EmailAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email already exists."


class VerificationCodeIncorrectException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid confirmation code"


class InvalidTokenException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail="Invalid token error"


class TokenExpiredException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Token has expired"


class EmailNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Email not found"


class UserNotCreatedException(APIException):
    status = status.HTTP_406_NOT_ACCEPTABLE
    detail = "User not created"


class ExceedingNumberOfRequestsException(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Exceeded number of requests"
