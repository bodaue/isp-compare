from fastapi import HTTPException
from starlette import status


class AppException(HTTPException):
    status_code: int
    detail: str
    headers: dict[str, str] | None = None

    def __init__(
        self, detail: str | None = None, headers: dict[str, str] | None = None
    ) -> None:
        _detail = detail or self.detail
        _headers = headers or self.headers
        super().__init__(status_code=self.status_code, detail=_detail, headers=_headers)


# Authentication Exceptions
class InvalidCredentialsException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid username or password"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenExpiredException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has expired"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenRevokedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Token has been revoked"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate credentials"
    headers = {"WWW-Authenticate": "Bearer"}


class RefreshTokenMissingException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Refresh token missing"
    headers = {"WWW-Authenticate": "Bearer"}


class UserNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"


class UsernameAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Username already registered"


class EmailAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Email already registered"


class IncorrectPasswordException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Current password is incorrect"
