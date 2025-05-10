from datetime import UTC, datetime
from uuid import UUID

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
    detail = "У вас нет прав администратора для выполнения этого действия."


class InvalidCredentialsException(AppException):
    detail = "Неверное имя пользователя или пароль."
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(
        self,
        remaining_attempts: int,
        max_attempts: int = 5,
        is_last_attempt: bool = False,
        retry_after: int | None = None,
    ) -> None:
        headers = {
            "WWW-Authenticate": "Bearer",
            "X-RateLimit-Limit": str(max_attempts),
            "X-RateLimit-Remaining": str(remaining_attempts),
        }

        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)

        detail = self.detail
        if is_last_attempt:
            detail = f"{self.detail}\nСлишком много попыток входа."

        super().__init__(status_code=self.status_code, detail=detail, headers=headers)


class TokenExpiredException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Срок действия токена истек."
    headers = {"WWW-Authenticate": "Bearer"}


class TokenRevokedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Токен был отозван."
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Не удалось проверить учетные данные."
    headers = {"WWW-Authenticate": "Bearer"}


class TokenSubjectMissingException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Недействительный токен: отсутствует идентификатор."
    headers = {"WWW-Authenticate": "Bearer"}


class RefreshTokenMissingException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Отсутствует токен обновления."
    headers = {"WWW-Authenticate": "Bearer"}


class UserNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Пользователь не найден."


class UsernameAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с таким именем уже зарегистрирован."


class EmailAlreadyExistsException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Пользователь с таким email уже зарегистрирован."


class IncorrectPasswordException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Текущий пароль неверный."


class ProviderNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Провайдер не найден."


class TariffNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Тариф не найден."


class TariffNotFoundByIdException(AppException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, tariff_id: UUID) -> None:
        detail = f"Тариф с ID {tariff_id} не найден"
        super().__init__(detail=detail)


class ReviewNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Отзыв не найден."


class SearchHistoryNotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "История поиска не найдена."


class RateLimitExceededException(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Превышен лимит запросов. Пожалуйста, попробуйте позже."


class LoginRateLimitExceededException(RateLimitExceededException):
    detail = "Слишком много попыток входа."

    def __init__(self, retry_after: int = 300) -> None:  # 5 минут по умолчанию
        headers = {
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": "5",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(datetime.now(UTC).timestamp()) + retry_after),
        }
        super().__init__(headers=headers)


class PasswordChangeRateLimitExceededException(RateLimitExceededException):
    detail = "Слишком много попыток смены пароля. Пожалуйста, попробуйте позже."


class TokenRefreshRateLimitExceededException(RateLimitExceededException):
    detail = "Слишком много попыток обновления токена. Пожалуйста, попробуйте позже."


class UsernameChangeRateLimitExceededException(RateLimitExceededException):
    detail = (
        "Слишком много попыток изменения имени пользователя. "
        "Пожалуйста, попробуйте позже."
    )
