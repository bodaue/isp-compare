import re
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from isp_compare.schemas.tariff import TariffCreate


class BaseParser(ABC):
    """Базовый абстрактный класс для парсеров провайдеров"""

    provider_name: str
    provider_id: UUID | None = None

    @abstractmethod
    async def parse_tariffs(self) -> list[TariffCreate]:
        """
        Парсинг тарифов с сайта провайдера

        Returns:
            List[TariffCreate]: Список тарифов в формате для создания в БД
        """

    @abstractmethod
    async def parse_tariff_details(self, tariff_url: str) -> dict[str, Any]:
        """
        Парсинг деталей конкретного тарифа

        Args:
            tariff_url: URL тарифа для получения деталей

        Returns:
            Dict[str, Any]: Детали тарифа
        """

    @staticmethod
    def clean_price(price_str: str) -> float:
        """
        Очистка строки с ценой и преобразование в float

        Args:
            price_str: Строка с ценой (например, '299 ₽/мес')

        Returns:
            float: Числовое значение цены
        """
        import re

        # Удаляем всё, кроме цифр и точек
        cleaned = re.sub(r"[^\d.]", "", price_str.replace(",", "."))
        return float(cleaned) if cleaned else 0.0

    @staticmethod
    def clean_speed(speed_str: str) -> int:
        """
        Очистка строки со скоростью и преобразование в int

        Args:
            speed_str: Строка со скоростью (например, 'до 100 Мбит/с')

        Returns:
            int: Числовое значение скорости
        """

        numbers = re.findall(r"\d+", speed_str)
        return int(numbers[0]) if numbers else 0
