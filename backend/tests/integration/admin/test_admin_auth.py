from httpx import AsyncClient

from isp_compare.models.user import User


async def test_admin_login_success(
    admin_page_client: AsyncClient, admin_user: User
) -> None:
    login_data = {
        "username": admin_user.username,
        "password": "AdminPassword123!",
    }

    response = await admin_page_client.post("/admin/login", data=login_data)
    assert response.status_code == 302
    assert "session" in response.cookies


async def test_admin_login_wrong_password(
    admin_page_client: AsyncClient, admin_user: User
) -> None:
    login_data = {
        "username": admin_user.username,
        "password": "WrongPassword",
    }

    response = await admin_page_client.post("/admin/login", data=login_data)
    assert response.status_code == 400


async def test_admin_login_regular_user(
    admin_page_client: AsyncClient, regular_user: User
) -> None:
    login_data = {
        "username": regular_user.username,
        "password": "Password123!",
    }

    response = await admin_page_client.post("/admin/login", data=login_data)
    assert response.status_code == 400


async def test_admin_logout(admin_page_client: AsyncClient, admin_user: User) -> None:
    login_data = {
        "username": admin_user.username,
        "password": "AdminPassword123!",
    }
    login_response = await admin_page_client.post("/admin/login", data=login_data)
    assert login_response.status_code == 302

    response = await admin_page_client.get("/admin/logout")
    assert response.status_code == 302

    logout_cookies = response.cookies
    login_cookies = login_response.cookies

    if "session" in logout_cookies and "session" in login_cookies:
        assert logout_cookies["session"] != login_cookies["session"]


async def test_admin_access_without_auth(admin_page_client: AsyncClient) -> None:
    response = await admin_page_client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login" in response.headers.get("location", "")

    response = await admin_page_client.get("/admin/providers/list")
    assert response.status_code == 302
    assert "/admin/login" in response.headers.get("location", "")


async def test_admin_access_after_login(
    admin_page_client: AsyncClient, admin_user: User
) -> None:
    login_data = {
        "username": admin_user.username,
        "password": "AdminPassword123!",
    }

    login_response = await admin_page_client.post("/admin/login", data=login_data)
    assert login_response.status_code == 302

    response = await admin_page_client.get("/admin/")
    assert response.status_code == 200

    response = await admin_page_client.get("/admin/provider/list")
    assert response.status_code == 200
