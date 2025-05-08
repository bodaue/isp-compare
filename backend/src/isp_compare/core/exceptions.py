from fastapi import HTTPException
from starlette import status


class AppException(HTTPException):
    status_code: int
    detail: str
    headers: dict[str, str] | None = None

    def __init__(
        self,
        status_code: int | None = None,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        _status_code = status_code or self.status_code
        _detail = detail or self.detail
        _headers = headers or self.headers
        super().__init__(status_code=_status_code, detail=_detail, headers=_headers)


class AdminAccessDeniedException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "У вас нет прав администратора для выполнения этого действия"


class InvalidCredentialsException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Неверное имя пользователя или пароль"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenExpiredException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenRevokedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен был отозван"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Не удалось проверить учетные данные"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenSubjectMissingException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Недействительный токен: отсутствует идентификатор"
    headers = {"WWW-Authenticate": "Bearer"}


class RefreshTokenMissingException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Отсутствует токен обновления"
    headers = {"WWW-Authenticate": "Bearer"}


class UserNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден"


class UsernameAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с таким именем уже зарегистрирован"


class EmailAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с таким email уже зарегистрирован"


class IncorrectPasswordException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Текущий пароль неверный"


class ProviderNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Провайдер не найден"


class TariffNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Тариф не найден"


class ReviewNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Отзыв не найден"


class SearchHistoryNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "История поиска не найдена"


class RateLimitExceededException(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Превышен лимит запросов. Пожалуйста, попробуйте позже."


class LoginRateLimitExceededException(RateLimitExceededException):
    detail = "Слишком много попыток входа. Пожалуйста, попробуйте позже."


class PasswordChangeRateLimitExceededException(RateLimitExceededException):
    detail = "Слишком много попыток смены пароля. Пожалуйста, попробуйте позже."


class TokenRefreshRateLimitExceededException(RateLimitExceededException):
    detail = "Слишком много попыток обновления токена. Пожалуйста, попробуйте позже."


class UsernameChangeRateLimitExceededException(RateLimitExceededException):
    detail = (
        "Слишком много попыток изменения имени пользователя. "
        "Пожалуйста, попробуйте позже."
    )
