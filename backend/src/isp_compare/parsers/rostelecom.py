import asyncio
import logging
import re
from decimal import Decimal

import httpx
from bs4 import BeautifulSoup

from isp_compare.parsers.base import BaseParser
from isp_compare.schemas.tariff import TariffCreate

logger = logging.getLogger(__name__)


class RostelecomParser(BaseParser):
    provider_name = "Ростелеком"
    base_url = "https://volgograd.rt.ru"
    tariffs_url = "https://volgograd.rt.ru/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
        "image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    async def parse_tariffs(self) -> list[TariffCreate]:
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(self.tariffs_url)
            soup = BeautifulSoup(response.text, "html.parser")
            tariffs = []

            tariff_containers = soup.select(".tariff-card")

            for container in tariff_containers:
                try:
                    name = container.select_one(".tariff-title").text.strip()
                    price_text = container.select_one(".tariff-price").text.strip()
                    price = self.clean_price(price_text)

                    speed_text = container.select_one(".tariff-speed").text.strip()
                    speed = self.clean_speed(speed_text)

                    description = container.select_one(
                        ".tariff-description"
                    ).text.strip()

                    features_text = container.select_one(
                        ".tariff-features"
                    ).text.lower()
                    has_tv = "тв" in features_text or "телевидение" in features_text
                    has_phone = "телефон" in features_text

                    tariff_link = container.select_one("a.tariff-link")
                    url = self.base_url + tariff_link["href"] if tariff_link else None

                    promo_price = None
                    promo_period = None
                    promo_container = container.select_one(".tariff-promo")
                    if promo_container:
                        promo_price_text = promo_container.select_one(
                            ".promo-price"
                        ).text.strip()
                        promo_price = self.clean_price(promo_price_text)

                        promo_period_text = promo_container.select_one(
                            ".promo-period"
                        ).text.strip()
                        promo_period_match = re.search(r"\d+", promo_period_text)
                        promo_period = (
                            int(promo_period_match.group(0))
                            if promo_period_match
                            else None
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


if __name__ == "__main__":
    a = RostelecomParser()
    asyncio.run(a.parse_tariffs())
