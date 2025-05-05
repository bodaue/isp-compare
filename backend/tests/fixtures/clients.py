from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client(fastapi_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def auth_client(
    user_token: str, fastapi_app: FastAPI
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
        follow_redirects=True,
        headers={"Authorization": f"Bearer {user_token}"},
    ) as client:
        yield client


@pytest.fixture
async def admin_client(
    admin_token: str, fastapi_app: FastAPI
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
        follow_redirects=True,
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as client:
        yield client
