import re
from abc import ABC, abstractmethod
from uuid import UUID

from isp_compare.schemas.tariff import TariffCreate


class BaseParser(ABC):
    provider_name: str
    provider_id: UUID | None = None

    @abstractmethod
    async def parse_tariffs(self) -> list[TariffCreate]:
        pass

    @staticmethod
    def clean_price(price_str: str) -> float:
        cleaned = re.sub(r"[^\d.]", "", price_str.replace(",", "."))
        return float(cleaned) if cleaned else 0.0

    @staticmethod
    def clean_speed(speed_str: str) -> int:
        numbers = re.findall(r"\d+", speed_str)
        return int(numbers[0]) if numbers else 0
