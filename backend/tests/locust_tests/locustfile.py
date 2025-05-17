import secrets
from typing import Any

from locust import HttpUser, TaskSet, between, task


class UserBehavior(TaskSet):
    access_token: str | None = None
    provider_ids: list[str] = []
    tariff_ids: list[str] = []

    is_authenticated: bool = False

    def on_start(self) -> None:
        self.get_providers()

    @task(1)
    def try_authenticate(self) -> None:
        if self.is_authenticated:
            return

        unique_id = secrets.token_hex(6)
        username = f"locust_user_{unique_id}"
        password = "Password123!"

        register_data = {
            "fullname": f"Test User {username}",
            "username": username,
            "password": password,
            "email": f"{username}@example.com",
        }

        with self.client.post(
            "/api/auth/register", json=register_data, catch_response=True
        ) as response:
            if response.status_code == 201:
                response_data = response.json()
                self.access_token = response_data.get("access_token")
                self.is_authenticated = True
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                login_data = {"username": username, "password": password}

                login_response = self.client.post(
                    "/api/auth/login", json=login_data, catch_response=True
                )

                try:
                    if login_response.status_code == 200:
                        response_data = login_response.json()
                        self.access_token = response_data.get("access_token")
                        self.is_authenticated = True
                        login_response.success()
                    elif login_response.status_code == 429:
                        login_response.success()
                    else:
                        login_response.failure(
                            f"Ошибка аутентификации: {login_response.text}"
                        )
                finally:
                    if hasattr(login_response, "close"):
                        login_response.close()

    @task(20)
    def get_providers(self) -> None:
        with self.client.get("/api/providers", catch_response=True) as response:
            if response.status_code == 200:
                providers = response.json()
                if providers:
                    self.provider_ids = [provider["id"] for provider in providers]
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Ошибка при получении провайдеров: {response.text}")

    @task(20)
    def get_provider_tariffs(self) -> None:
        if not self.provider_ids:
            return

        provider_id = self.provider_ids[secrets.randbelow(len(self.provider_ids))]

        with self.client.get(
            f"/api/providers/{provider_id}/tariffs", catch_response=True
        ) as response:
            if response.status_code == 200:
                tariffs = response.json()
                if tariffs:
                    for tariff in tariffs:
                        if tariff["id"] not in self.tariff_ids:
                            self.tariff_ids.append(tariff["id"])
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Ошибка при получении тарифов: {response.text}")

    @task(8)
    def search_tariffs(self) -> None:
        if not self.is_authenticated:
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}

        price_options = [None, 20, 30, 40]
        max_price_options = [None, 50, 80, 100]
        speed_options = [None, 50, 100, 200]
        max_speed_options = [None, 500, 800, 1000]
        bool_options = [None, True, False]

        search_params: dict[str, Any] = {
            "min_price": price_options[secrets.randbelow(len(price_options))],
            "max_price": max_price_options[secrets.randbelow(len(max_price_options))],
            "min_speed": speed_options[secrets.randbelow(len(speed_options))],
            "max_speed": max_speed_options[secrets.randbelow(len(max_speed_options))],
            "has_tv": bool_options[secrets.randbelow(len(bool_options))],
            "has_phone": bool_options[secrets.randbelow(len(bool_options))],
        }

        search_params = {k: v for k, v in search_params.items() if v is not None}

        with self.client.get(
            "/api/tariffs/search",
            params=search_params,
            headers=headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                tariffs = response.json()
                if tariffs:
                    for tariff in tariffs:
                        if tariff["id"] not in self.tariff_ids:
                            self.tariff_ids.append(tariff["id"])
                response.success()
            elif response.status_code in [401, 429]:
                response.success()
            else:
                response.failure(f"Ошибка при поиске тарифов: {response.text}")

    @task(8)
    def compare_tariffs(self) -> None:
        if len(self.tariff_ids) < 2:
            return

        num_tariffs = min(len(self.tariff_ids), 2 + secrets.randbelow(3))

        tariff_ids_to_compare = []
        available_indices = list(range(len(self.tariff_ids)))
        for _ in range(num_tariffs):
            if not available_indices:
                break
            idx = secrets.randbelow(len(available_indices))
            selected_idx = available_indices.pop(idx)
            tariff_ids_to_compare.append(self.tariff_ids[selected_idx])

        comparison_data = {"tariff_ids": tariff_ids_to_compare}

        with self.client.post(
            "/api/tariffs/comparison", json=comparison_data, catch_response=True
        ) as response:
            if response.status_code in [200, 429]:
                response.success()
            else:
                response.failure(f"Ошибка при сравнении тарифов: {response.text}")

    @task(10)
    def get_search_history(self) -> None:
        if not self.is_authenticated:
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}

        with self.client.get(
            "/api/search-history", headers=headers, catch_response=True
        ) as response:
            if response.status_code in [200, 401, 429]:
                response.success()
            else:
                response.failure(
                    f"Ошибка при получении истории поиска: {response.text}"
                )

    @task(4)
    def add_or_update_review(self) -> None:
        if not self.is_authenticated or not self.provider_ids:
            return

        provider_id = self.provider_ids[secrets.randbelow(len(self.provider_ids))]

        quality_rating = secrets.randbelow(10) + 1
        support_time = secrets.randbelow(30) + 1

        review_data = {
            "rating": secrets.randbelow(5) + 1,
            "comment": f"Автотест: Отзыв о провайдере. "
            f"Качество связи {quality_rating}/10. "
            f"Скорость стабильная, техподдержка отвечает за {support_time} минут.",
        }

        headers = {"Authorization": f"Bearer {self.access_token}"}

        with self.client.post(
            f"/api/providers/{provider_id}/reviews",
            json=review_data,
            headers=headers,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201, 401, 429]:
                response.success()
            else:
                response.failure(f"Ошибка при добавлении отзыва: {response.text}")

    @task(20)
    def get_provider_reviews(self) -> None:
        if not self.provider_ids:
            return

        provider_id = self.provider_ids[secrets.randbelow(len(self.provider_ids))]

        with self.client.get(
            f"/api/providers/{provider_id}/reviews", catch_response=True
        ) as response:
            if response.status_code in [200, 429]:
                response.success()
            else:
                response.failure(f"Ошибка при получении отзывов: {response.text}")

    @task(1)
    def refresh_token(self) -> None:
        if not self.is_authenticated:
            return

        with self.client.post("/api/auth/refresh", catch_response=True) as response:
            if response.status_code in [200, 429]:
                if response.status_code == 200:
                    response_data = response.json()
                    self.access_token = response_data.get("access_token")
                response.success()
            else:
                self.access_token = None
                self.is_authenticated = False
                response.success()


class ISPCompareUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
