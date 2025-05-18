import logging
import re
from decimal import Decimal

import httpx
from bs4 import BeautifulSoup

from isp_compare.parsers.base import BaseParser
from isp_compare.schemas.tariff import TariffCreate

logger = logging.getLogger(__name__)


class DomruParser(BaseParser):
    provider_name = "Дом.ру"
    base_url = "https://volgograd.dom.ru"
    tariffs_url = "https://volgograd.dom.ru/internet"

    async def parse_tariffs(self) -> list[TariffCreate]:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.tariffs_url)
            soup = BeautifulSoup(response.text, "html.parser")

            tariffs = []

            tariff_containers = soup.select(".tariff-item")

            for container in tariff_containers:
                try:
                    name = container.select_one(".tariff-name").text.strip()
                    price_text = container.select_one(".tariff-price").text.strip()
                    price = self.clean_price(price_text)

                    speed_text = container.select_one(".tariff-speed").text.strip()
                    speed = self.clean_speed(speed_text)

                    description = container.select_one(".tariff-desc").text.strip()

                    features_text = container.select_one(
                        ".tariff-features"
                    ).text.lower()
                    has_tv = "тв" in features_text or "телевидение" in features_text
                    has_phone = "телефон" in features_text

                    tariff_link = container.select_one("a.tariff-more")
                    url = self.base_url + tariff_link["href"] if tariff_link else None

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
                        connection_cost=Decimal("0"),
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
