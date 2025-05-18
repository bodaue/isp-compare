import logging
import re
from decimal import Decimal
from typing import Any

import httpx
from bs4 import BeautifulSoup

from isp_compare.parsers.base import BaseParser
from isp_compare.schemas.tariff import TariffCreate

logger = logging.getLogger(__name__)


class BeelineParser(BaseParser):
    """Парсер для провайдера Билайн"""

    provider_name = "Билайн"
    base_url = "https://moskva.beeline.ru"
    tariffs_url = "https://moskva.beeline.ru/customers/products/home/"

    async def parse_tariffs(self) -> list[TariffCreate]:
        """Парсинг тарифов Билайн"""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.tariffs_url)
            soup = BeautifulSoup(response.text, "html.parser")

            tariffs = []
            # Селектор для контейнеров с тарифами (нужно адаптировать под реальный сайт)
            tariff_containers = soup.select(".tariff-card")

            for container in tariff_containers:
                try:
                    name = container.select_one(".tariff-name").text.strip()
                    price_text = container.select_one(".tariff-price").text.strip()
                    price = self.clean_price(price_text)

                    speed_text = container.select_one(".tariff-speed").text.strip()
                    speed = self.clean_speed(speed_text)

                    description = container.select_one(
                        ".tariff-description"
                    ).text.strip()

                    # Определение наличия ТВ и телефона
                    features_text = container.text.lower()
                    has_tv = "тв" in features_text or "телевидение" in features_text
                    has_phone = "телефон" in features_text

                    # URL тарифа для деталей
                    tariff_link = container.select_one("a.tariff-detail")
                    url = self.base_url + tariff_link["href"] if tariff_link else None

                    # Проверка на акционную цену
                    promo_block = container.select_one(".tariff-promo")
                    promo_price = None
                    promo_period = None

                    if promo_block:
                        promo_price_text = promo_block.select_one(
                            ".promo-price"
                        ).text.strip()
                        promo_price = self.clean_price(promo_price_text)

                        period_text = promo_block.select_one(
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
                        connection_cost=Decimal("0"),  # Уточнится позже
                        promo_price=Decimal(str(promo_price)) if promo_price else None,
                        promo_period=promo_period,
                        is_active=True,
                        url=url,
                    )

                    tariffs.append(tariff)
                except (KeyError, AttributeError, ValueError, TypeError) as e:
                    # Ловим конкретные исключения вместо общего Exception
                    logger.exception(f"Error parsing tariff: {e}")
                    continue

            return tariffs

    async def parse_tariff_details(self, tariff_url: str) -> dict[str, Any]:
        """Парсинг детальной информации о тарифе"""
        async with httpx.AsyncClient() as client:
            response = await client.get(tariff_url)
            soup = BeautifulSoup(response.text, "html.parser")

            details = {}

            # Извлечение информации о стоимости подключения
            connection_info = soup.select_one(".connection-info")
            if connection_info:
                cost_text = connection_info.select_one(".cost").text.strip()
                details["connection_cost"] = self.clean_price(cost_text)

            # Другие детали

            return details
