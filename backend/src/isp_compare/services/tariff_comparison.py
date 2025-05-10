from typing import Any
from uuid import UUID

from isp_compare.core.exceptions import TariffNotFoundException
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.tariff import TariffRepository
from isp_compare.schemas.provider import ProviderResponse
from isp_compare.schemas.tariff import TariffResponse
from isp_compare.schemas.tariff_comparison import (
    TariffComparisonItem,
    TariffComparisonResponse,
)


class TariffComparisonService:
    def __init__(
        self,
        tariff_repository: TariffRepository,
        provider_repository: ProviderRepository,
    ) -> None:
        self._tariff_repository = tariff_repository
        self._provider_repository = provider_repository

    async def compare_tariffs(self, tariff_ids: list[UUID]) -> TariffComparisonResponse:
        """Сравнение тарифов по ключевым параметрам"""
        tariffs_data = []
        comparison_matrix = {
            "price": [],
            "speed": [],
            "has_tv": [],
            "has_phone": [],
            "connection_cost": [],
            "value_for_money": [],
        }

        # Получаем данные о тарифах
        for tariff_id in tariff_ids:
            tariff = await self._tariff_repository.get_by_id(tariff_id)
            if not tariff:
                raise TariffNotFoundException

            provider, _ = await self._provider_repository.get_by_id(tariff.provider_id)

            # Рассчитываем эффективную цену
            effective_price = float(
                tariff.promo_price if tariff.promo_price else tariff.price
            )

            # Соотношение цена/качество (Мбит/с на рубль)
            value_for_money = (
                tariff.speed / effective_price if effective_price > 0 else 0
            )

            # Собираем характеристики
            characteristics = {
                "price": effective_price,
                "speed": tariff.speed,
                "has_tv": tariff.has_tv,
                "has_phone": tariff.has_phone,
                "connection_cost": float(tariff.connection_cost),
                "value_for_money": round(value_for_money, 2),
            }

            # Заполняем матрицу сравнения
            for key, value in characteristics.items():
                comparison_matrix[key].append(value)

            tariffs_data.append(
                {
                    "tariff": tariff,
                    "provider": provider,
                    "characteristics": characteristics,
                }
            )

        # Анализируем преимущества и недостатки
        comparison_items = []
        for _, data in enumerate(tariffs_data):
            advantages = self._analyze_advantages(
                data["characteristics"], comparison_matrix
            )
            disadvantages = self._analyze_disadvantages(
                data["characteristics"], comparison_matrix
            )

            comparison_items.append(
                TariffComparisonItem(
                    tariff=TariffResponse.model_validate(data["tariff"]),
                    provider=ProviderResponse.model_validate(data["provider"]),
                    characteristics=data["characteristics"],
                    advantages=advantages,
                    disadvantages=disadvantages,
                )
            )

        # Определяем лучшие тарифы
        best_by_price = tariff_ids[
            comparison_matrix["price"].index(min(comparison_matrix["price"]))
        ]
        best_by_speed = tariff_ids[
            comparison_matrix["speed"].index(max(comparison_matrix["speed"]))
        ]
        best_overall = tariff_ids[
            comparison_matrix["value_for_money"].index(
                max(comparison_matrix["value_for_money"])
            )
        ]

        # Формируем общий вывод
        summary = self._generate_comparison_summary(comparison_items, comparison_matrix)

        return TariffComparisonResponse(
            tariffs=comparison_items,
            comparison_matrix=comparison_matrix,
            best_by_price=best_by_price,
            best_by_speed=best_by_speed,
            best_overall=best_overall,
            summary=summary,
        )

    def _analyze_advantages(
        self, characteristics: dict[str, Any], matrix: dict[str, list]
    ) -> list[str]:
        """Анализ преимуществ тарифа"""
        advantages = []

        # Цена
        if characteristics["price"] == min(matrix["price"]):
            advantages.append("Самая низкая цена")

        # Скорость
        if characteristics["speed"] == max(matrix["speed"]):
            advantages.append("Максимальная скорость")

        # Дополнительные услуги
        if characteristics["has_tv"] and not all(matrix["has_tv"]):
            advantages.append("Включено ТВ")
        if characteristics["has_phone"] and not all(matrix["has_phone"]):
            advantages.append("Включена телефония")

        # Подключение
        if characteristics["connection_cost"] == 0:
            advantages.append("Бесплатное подключение")
        elif characteristics["connection_cost"] == min(matrix["connection_cost"]):
            advantages.append("Самая низкая стоимость подключения")

        # Соотношение цена/качество
        if characteristics["value_for_money"] == max(matrix["value_for_money"]):
            advantages.append("Лучшее соотношение цена/качество")

        return advantages

    def _analyze_disadvantages(
        self, characteristics: dict[str, Any], matrix: dict[str, list]
    ) -> list[str]:
        """Анализ недостатков тарифа"""
        disadvantages = []

        # Цена
        if characteristics["price"] == max(matrix["price"]):
            disadvantages.append("Самая высокая цена")

        # Скорость
        if characteristics["speed"] == min(matrix["speed"]):
            disadvantages.append("Минимальная скорость")

        # Подключение
        if (
            characteristics["connection_cost"] == max(matrix["connection_cost"])
            and characteristics["connection_cost"] > 0
        ):
            disadvantages.append("Самое дорогое подключение")

        # Соотношение цена/качество
        if characteristics["value_for_money"] == min(matrix["value_for_money"]):
            disadvantages.append("Худшее соотношение цена/качество")

        return disadvantages

    def _generate_comparison_summary(
        self, items: list[TariffComparisonItem], matrix: dict
    ) -> str:
        """Генерация текстового резюме сравнения"""
        price_diff = max(matrix["price"]) - min(matrix["price"])
        speed_diff = max(matrix["speed"]) - min(matrix["speed"])

        summary = f"Сравнение {len(items)} тарифов показало: "
        summary += f"разброс цен составляет {price_diff:.0f} руб., "
        summary += f"разница в скорости достигает {speed_diff} Мбит/с. "

        # Лучший по соотношению цена/качество
        best_overall_idx = matrix["value_for_money"].index(
            max(matrix["value_for_money"])
        )
        best_tariff = items[best_overall_idx]

        summary += (
            f"Наилучшее соотношение цена/качество у тарифа '{best_tariff.tariff.name}' "
        )
        summary += f"от {best_tariff.provider.name} "
        summary += (
            f"({best_tariff.characteristics['value_for_money']:.2f} Мбит/с на рубль)."
        )

        return summary
