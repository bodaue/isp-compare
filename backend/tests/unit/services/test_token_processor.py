from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from jose import JWTError, jwt

from isp_compare.core.config import JWTConfig
from isp_compare.core.exceptions import TokenSubjectMissingException
from isp_compare.services.token_processor import TokenProcessor


@pytest.fixture
def token_processor(jwt_config: JWTConfig) -> TokenProcessor:
    return TokenProcessor(jwt_config)


def test_create_access_token(token_processor: TokenProcessor) -> None:
    user_id = UUID("12345678-1234-1234-1234-123456789012")
    token = token_processor.create_access_token(user_id)

    payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])

    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    assert "iat" in payload
    assert datetime.fromtimestamp(payload["exp"], UTC) > datetime.now(UTC)


def test_create_refresh_token(token_processor: TokenProcessor) -> None:
    token, expires_at = token_processor.create_refresh_token()

    assert isinstance(token, str)
    assert len(token) == 64
    assert isinstance(expires_at, datetime)
    assert expires_at > datetime.now(UTC)
    # Verify it expires in approximately 7 days
    expected_expiry = datetime.now(UTC) + timedelta(days=7)
    assert abs((expires_at - expected_expiry).total_seconds()) < 5  # Within 5 seconds


def test_get_user_id_from_token(token_processor: TokenProcessor) -> None:
    user_id = UUID("12345678-1234-1234-1234-123456789012")
    token = token_processor.create_access_token(user_id)

    extracted_id = token_processor.get_user_id_from_token(token)
    assert extracted_id == user_id


def test_get_user_id_from_token_missing_subject(
    token_processor: TokenProcessor,
) -> None:
    token = jwt.encode(
        {"exp": datetime.now(UTC) + timedelta(minutes=30)},
        "test_secret_key",
        algorithm="HS256",
    )

    with pytest.raises(TokenSubjectMissingException):
        token_processor.get_user_id_from_token(token)


def test_decode_token_invalid_signature(token_processor: TokenProcessor) -> None:
    user_id = UUID("12345678-1234-1234-1234-123456789012")
    token = jwt.encode(
        {"sub": str(user_id), "exp": datetime.now(UTC) + timedelta(minutes=30)},
        "wrong_secret_key",
        algorithm="HS256",
    )

    with pytest.raises(JWTError):
        token_processor.decode_token(token)


def test_decode_token_expired(token_processor: TokenProcessor) -> None:
    user_id = UUID("12345678-1234-1234-1234-123456789012")
    token = jwt.encode(
        {"sub": str(user_id), "exp": datetime.now(UTC) - timedelta(minutes=30)},
        "test_secret_key",
        algorithm="HS256",
    )

    with pytest.raises(JWTError):
        token_processor.decode_token(token)
