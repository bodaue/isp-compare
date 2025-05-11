from decimal import Decimal

from isp_compare.core.exceptions import TariffNotFoundByIdException
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.tariff import TariffRepository
from isp_compare.schemas.tariff_comparison import (
    ComparisonRequest,
    ComparisonResult,
    TariffComparisonItem,
)


class TariffComparisonService:
    def __init__(
        self,
        tariff_repository: TariffRepository,
        provider_repository: ProviderRepository,
    ) -> None:
        self._tariff_repository = tariff_repository
        self._provider_repository = provider_repository

    async def compare_tariffs(self, request: ComparisonRequest) -> ComparisonResult:
        tariff_ids = list(set(request.tariff_ids))
        tariff_map = await self._tariff_repository.get_multiple_by_ids(tariff_ids)

        # Проверяем, что все запрошенные тарифы найдены
        for tariff_id in tariff_ids:
            if tariff_id not in tariff_map:
                raise TariffNotFoundByIdException(tariff_id)

        # Получаем провайдеров
        provider_ids = [tariff.provider_id for tariff in tariff_map.values()]
        provider_map = await self._provider_repository.get_multiple_by_ids(provider_ids)

        # Преобразуем тарифы в элементы сравнения
        comparison_items = []
        for tariff_id in tariff_ids:
            tariff = tariff_map[tariff_id]
            provider_name = provider_map.get(tariff.provider_id).name

            # Определяем актуальную и оригинальную цену
            current_price = (
                float(tariff.promo_price)
                if tariff.promo_price is not None
                else float(tariff.price)
            )
            original_price = float(tariff.price)

            # Формируем список особенностей
            features = []
            if tariff.has_tv:
                features.append("ТВ")
            if tariff.has_phone:
                features.append("Телефон")
            if tariff.connection_cost is not None and tariff.connection_cost == 0:
                features.append("Бесплатное подключение")

            # Рассчитываем метрики
            price_per_mbps = Decimal(str(current_price / tariff.speed))
            yearly_cost = Decimal(str(current_price * 12))
            value_score = self._calculate_value_score(
                Decimal(str(current_price)),
                tariff.speed,
                len(features),
                tariff.connection_cost,
            )

            comparison_items.append(
                TariffComparisonItem(
                    id=tariff.id,
                    name=tariff.name,
                    provider_name=provider_name,
                    current_price=Decimal(str(current_price)),
                    original_price=Decimal(str(original_price)),
                    is_promo=tariff.promo_price is not None,
                    promo_period=tariff.promo_period,
                    speed=tariff.speed,
                    features=features,
                    connection_cost=(
                        Decimal(str(tariff.connection_cost))
                        if tariff.connection_cost is not None
                        else None
                    ),
                    price_per_mbps=price_per_mbps,
                    yearly_cost=yearly_cost,
                    value_score=value_score,
                )
            )

        # Определяем лучшие тарифы
        self._mark_best_tariffs(comparison_items)

        # Генерируем рекомендации
        recommendations = self._generate_recommendations(comparison_items)

        # Создаем краткое резюме
        summary = self._generate_summary(comparison_items)

        return ComparisonResult(
            items=comparison_items,
            recommendations=recommendations,
            summary=summary,
        )

    def _calculate_value_score(
        self,
        price: Decimal,
        speed: int,
        features_count: int,
        connection_cost: Decimal | None,
    ) -> Decimal:
        """Расчет комплексной оценки ценности тарифа"""
        # Базовый score = цена за Мбит/с
        score = price / speed

        # Бонус за дополнительные услуги (5% за каждую)
        if features_count > 0:
            score *= Decimal(str(1 - 0.05 * features_count))

        # Штраф за высокую стоимость подключения
        if connection_cost is not None and connection_cost > 0:
            score *= 1 + connection_cost / 10000

        return score

    def _mark_best_tariffs(self, items: list[TariffComparisonItem]) -> None:
        """Маркировка лучших тарифов по разным критериям"""
        if not items:
            return

        # Самый дешевый
        min_price = min(item.current_price for item in items)
        for item in items:
            if item.current_price == min_price:
                item.is_cheapest = True

        # Самый быстрый
        max_speed = max(item.speed for item in items)
        for item in items:
            if item.speed == max_speed:
                item.is_fastest = True

        # Лучшее соотношение цена/качество
        min_value_score = min(item.value_score for item in items)
        for item in items:
            if item.value_score == min_value_score:
                item.is_best_value = True

        # Больше всего возможностей
        max_features = max(len(item.features) for item in items)
        for item in items:
            if len(item.features) == max_features:
                item.has_most_features = True

    def _generate_recommendations(self, items: list[TariffComparisonItem]) -> list[str]:
        """Генерация персонализированных рекомендаций"""
        recommendations = []

        # Находим лучшие тарифы
        cheapest = next(item for item in items if item.is_cheapest)
        fastest = next(item for item in items if item.is_fastest)
        best_value = next(item for item in items if item.is_best_value)

        # Основные рекомендации
        recommendations.append(
            f"Самый доступный: {cheapest.name} ({cheapest.provider_name}) - "
            f"{cheapest.current_price} ₽/мес"
        )

        if fastest != cheapest:
            price_diff = fastest.current_price - cheapest.current_price
            speed_diff = fastest.speed - cheapest.speed
            recommendations.append(
                f"Самый быстрый: {fastest.name} ({fastest.provider_name}) - "
                f"{fastest.speed} Мбит/с (+{speed_diff} Мбит/с, +{price_diff} ₽/мес)"
            )

        if best_value not in (cheapest, fastest):
            recommendations.append(
                f"Оптимальный выбор: {best_value.name} ({best_value.provider_name}) - "
                f"лучшее соотношение цены и качества"
            )

        # Акционные предложения
        promo_items = [item for item in items if item.is_promo]
        if promo_items:
            best_promo = max(
                promo_items, key=lambda x: x.original_price - x.current_price
            )
            discount = best_promo.original_price - best_promo.current_price
            recommendations.append(
                f"Лучшая акция: {best_promo.name} - скидка {discount} ₽/мес "
                f"(цена {best_promo.current_price} ₽ вместо "
                f"{best_promo.original_price} ₽)"
            )

        # Дополнительные услуги
        with_tv = [item for item in items if "ТВ" in item.features]
        if with_tv and len(with_tv) < len(items):
            cheapest_with_tv = min(with_tv, key=lambda x: x.current_price)
            recommendations.append(
                f"С телевидением: {cheapest_with_tv.name} - "
                f"самый доступный с ТВ ({cheapest_with_tv.current_price} ₽/мес)"
            )

        # Бесплатное подключение
        free_connection = [
            item for item in items if "Бесплатное подключение" in item.features
        ]
        if free_connection and len(free_connection) < len(items):
            recommendations.append(
                f"Без затрат на подключение: "
                f"{', '.join(item.name for item in free_connection)}"
            )

        return recommendations

    def _generate_summary(self, items: list[TariffComparisonItem]) -> str:
        """Генерация краткого резюме сравнения"""
        cheapest = next(item for item in items if item.is_cheapest)
        fastest = next(item for item in items if item.is_fastest)

        price_diff = max(item.current_price for item in items) - min(
            item.current_price for item in items
        )
        speed_diff = max(item.speed for item in items) - min(
            item.speed for item in items
        )

        return (
            f"Сравнение {len(items)} тарифов: "
            f"разница в цене {price_diff} ₽, в скорости {speed_diff} Мбит/с. "
            f"Самый доступный - {cheapest.name} ({cheapest.current_price} ₽), "
            f"самый быстрый - {fastest.name} ({fastest.speed} Мбит/с)."
        )
