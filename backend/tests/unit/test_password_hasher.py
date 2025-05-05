import pytest

from isp_compare.services.password_hasher import PasswordHasher


@pytest.fixture
def password_hasher() -> PasswordHasher:
    return PasswordHasher()


@pytest.fixture
def test_password() -> str:
    return "SecurePassword123"


def test_password_hash_not_same_as_input(
    password_hasher: PasswordHasher, test_password: str
) -> None:
    hashed = password_hasher.hash(test_password)
    assert hashed != test_password
    assert isinstance(hashed, str)


def test_password_verify_success(
    password_hasher: PasswordHasher, test_password: str
) -> None:
    hashed = password_hasher.hash(test_password)
    assert password_hasher.verify(test_password, hashed) is True


def test_password_verify_failure(
    password_hasher: PasswordHasher, test_password: str
) -> None:
    hashed = password_hasher.hash(test_password)
    assert password_hasher.verify("WrongPassword", hashed) is False


def test_different_passwords_have_different_hashes(
    password_hasher: PasswordHasher,
) -> None:
    password1 = "Password123"
    password2 = "Password456"

    hash1 = password_hasher.hash(password1)
    hash2 = password_hasher.hash(password2)

    assert hash1 != hash2


def test_same_password_different_hashes(
    password_hasher: PasswordHasher, test_password: str
) -> None:
    hash1 = password_hasher.hash(test_password)
    hash2 = password_hasher.hash(test_password)
    assert hash1 != hash2  # Different due to different salts
