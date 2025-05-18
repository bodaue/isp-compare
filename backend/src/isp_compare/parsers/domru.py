import logging

import httpx
import re
from bs4 import BeautifulSoup
from typing import Any
from decimal import Decimal

from isp_compare.parsers.base import BaseParser
from isp_compare.schemas.tariff import TariffCreate

logger = logging.getLogger(__name__)


class DomruParser(BaseParser):
    """Парсер для провайдера Дом.ру"""

    provider_name = "Дом.ру"
    base_url = "https://domru.ru"
    tariffs_url = "https://domru.ru/internet/"

    async def parse_tariffs(self) -> list[TariffCreate]:
        """Парсинг тарифов Дом.ру"""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.tariffs_url)
            soup = BeautifulSoup(response.text, "html.parser")

            tariffs = []
            # Селектор для контейнеров с тарифами (нужно адаптировать под реальный сайт)
            tariff_containers = soup.select(".tariff-item")

            for container in tariff_containers:
                try:
                    name = container.select_one(".tariff-name").text.strip()
                    price_text = container.select_one(".tariff-price").text.strip()
                    price = self.clean_price(price_text)

                    speed_text = container.select_one(".tariff-speed").text.strip()
                    speed = self.clean_speed(speed_text)

                    description = container.select_one(".tariff-desc").text.strip()

                    # Определение наличия ТВ и телефона
                    features_text = container.select_one(
                        ".tariff-features"
                    ).text.lower()
                    has_tv = "тв" in features_text or "телевидение" in features_text
                    has_phone = "телефон" in features_text

                    # URL тарифа для деталей
                    tariff_link = container.select_one("a.tariff-more")
                    url = self.base_url + tariff_link["href"] if tariff_link else None

                    # Проверка на акционную цену
                    promo_container = container.select_one(".tariff-promo")
                    promo_price = None
                    promo_period = None

                    if promo_container:
                        promo_price_text = promo_container.select_one(
                            ".promo-price"
                        ).text.strip()
                        promo_price = self.clean_price(promo_price_text)

                        period_text = promo_container.select_one(
                            ".promo-period"
                        ).text.strip()
                        period_match = re.search(r"\d+", period_text)
                        promo_period = (
                            int(period_match.group(0)) if period_match else None
                        )

                    tariff = TariffCreate(
                        name=name,
                        description=description,
                        price=Decimal(str(price)),
                        speed=speed,
                        has_tv=has_tv,
                        has_phone=has_phone,
                        connection_cost=Decimal(
                            "0"
                        ),  # По умолчанию, обновится из деталей
                        promo_price=Decimal(str(promo_price)) if promo_price else None,
                        promo_period=promo_period,
                        is_active=True,
                        url=url,
                    )

                    tariffs.append(tariff)
                except (KeyError, AttributeError, ValueError, TypeError) as e:
                    logger.exception(f"Error parsing tariff: {e}")
                    continue

            return tariffs

    async def parse_tariff_details(self, tariff_url: str) -> dict[str, Any]:
        """Парсинг детальной информации о тарифе"""
        async with httpx.AsyncClient() as client:
            response = await client.get(tariff_url)
            soup = BeautifulSoup(response.text, "html.parser")

            details = {}

            # Извлечение детальной информации
            connection_block = soup.select_one(".connection-info")
            if connection_block:
                cost_text = connection_block.select_one(".connection-cost").text.strip()
                details["connection_cost"] = self.clean_price(cost_text)

            # Другие детали

            return details
