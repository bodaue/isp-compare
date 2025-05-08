from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.services.transaction_manager import TransactionManager


@pytest.fixture
def session_mock() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def transaction_manager(session_mock: AsyncMock) -> TransactionManager:
    return TransactionManager(session=session_mock)


async def test_commit(
    transaction_manager: TransactionManager,
    session_mock: AsyncMock,
) -> None:
    await transaction_manager.commit()

    session_mock.commit.assert_called_once()


async def test_flush(
    transaction_manager: TransactionManager,
    session_mock: AsyncMock,
) -> None:
    await transaction_manager.flush()

    session_mock.flush.assert_called_once()


async def test_rollback(
    transaction_manager: TransactionManager,
    session_mock: AsyncMock,
) -> None:
    await transaction_manager.rollback()

    session_mock.rollback.assert_called_once()


async def test_refresh(
    transaction_manager: TransactionManager,
    session_mock: AsyncMock,
) -> None:
    test_instance = object()

    await transaction_manager.refresh(test_instance)

    session_mock.refresh.assert_called_once_with(test_instance)


async def test_initialization(session_mock: AsyncMock) -> None:
    transaction_manager = TransactionManager(session=session_mock)

    assert transaction_manager.session is session_mock
