from fastapi import status


class APIException(Exception):
    status_code = None
    detail = None

    def __str__(self):
        return f"{self.detail}"


class EmailAlreadyExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Email already exists."


class ExceedingNumberOfRequestsException(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Exceeded number of requests"


class EmailNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Email not found"
