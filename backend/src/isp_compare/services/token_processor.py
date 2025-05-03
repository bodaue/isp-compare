import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from isp_compare.core.config import JWTConfig
from isp_compare.core.exceptions import TokenSubjectMissingException
from jose import jwt


class TokenProcessor:
    def __init__(self, jwt_config: JWTConfig) -> None:
        self._jwt_config = jwt_config

    def create_access_token(self, user_id: UUID) -> str:
        expire_at = datetime.now(UTC) + timedelta(
            minutes=self._jwt_config.access_token_expires_minutes
        )
        issued_at = datetime.now(UTC)

        to_encode = {
            "sub": str(user_id),
            "exp": expire_at,
            "iat": issued_at,
        }
        return jwt.encode(
            to_encode,
            self._jwt_config.secret_key.get_secret_value(),
            algorithm=self._jwt_config.algorithm,
        )

    def create_refresh_token(self) -> tuple[str, datetime]:
        token = secrets.token_hex(32)  # 64 character hex string
        expires_at = datetime.now(UTC) + timedelta(
            days=self._jwt_config.refresh_token_expires_days
        )
        return token, expires_at

    def decode_token(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self._jwt_config.secret_key.get_secret_value(),
            algorithms=[self._jwt_config.algorithm],
        )

    def get_user_id_from_token(self, token: str) -> UUID:
        payload = self.decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise TokenSubjectMissingException
        return UUID(user_id_str)
