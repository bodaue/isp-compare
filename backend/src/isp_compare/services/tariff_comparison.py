# backend/src/isp_compare/services/tariff_comparison.py

from decimal import Decimal

from isp_compare.core.exceptions import TariffNotFoundByIdException
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.tariff import TariffRepository
from isp_compare.schemas.tariff_comparison import (
    ComparisonRequest,
    ComparisonResult,
    FeatureComparison,
    PriceComparison,
    SpeedComparison,
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
        # Получаем все тарифы одним запросом
        tariff_map = await self._tariff_repository.get_multiple_by_ids(
            request.tariff_ids
        )

        # Проверяем, что все запрошенные тарифы найдены
        for tariff_id in request.tariff_ids:
            if tariff_id not in tariff_map:
                raise TariffNotFoundByIdException(tariff_id)

        provider_ids = [tariff.provider_id for tariff in tariff_map.values()]
        provider_map = await self._provider_repository.get_multiple_by_ids(provider_ids)

        # Преобразуем тарифы в элементы сравнения
        comparison_items = []
        for tariff_id in request.tariff_ids:
            tariff = tariff_map[tariff_id]

            provider_name = (
                provider_map.get(tariff.provider_id).name
                if tariff.provider_id in provider_map
                else None
            )

            effective_price = (
                float(tariff.promo_price)
                if tariff.promo_price is not None
                else float(tariff.price)
            )

            # Рассчитываем метрики
            price_per_mbps = Decimal(str(effective_price / tariff.speed))
            yearly_cost = Decimal(str(effective_price * 12))

            # Рассчитываем очки ценности
            value_score = self._calculate_value_score(
                Decimal(str(effective_price)),
                tariff.speed,
                tariff.has_tv,
                tariff.has_phone,
                Decimal(str(tariff.connection_cost)),
            )

            comparison_items.append(
                TariffComparisonItem(
                    id=tariff.id,
                    name=tariff.name,
                    provider_id=tariff.provider_id,
                    provider_name=provider_name,
                    base_price=Decimal(str(tariff.price)),
                    effective_price=Decimal(str(effective_price)),
                    speed=tariff.speed,
                    has_tv=tariff.has_tv,
                    has_phone=tariff.has_phone,
                    connection_cost=Decimal(str(tariff.connection_cost)),
                    is_promo=tariff.promo_price is not None,
                    promo_price=(
                        Decimal(str(tariff.promo_price))
                        if tariff.promo_price is not None
                        else None
                    ),
                    promo_period=tariff.promo_period,
                    price_per_mbps=price_per_mbps,
                    yearly_cost=yearly_cost,
                    value_score=value_score,
                )
            )

        # Определяем лучшие тарифы
        self._mark_best_tariffs(comparison_items)

        # Создаем детальные сравнения
        price_comparison = self._create_price_comparison(comparison_items)
        speed_comparison = self._create_speed_comparison(comparison_items)
        feature_comparison = self._create_feature_comparison(comparison_items)

        # Вычисляем только необходимую статистику
        prices = [item.effective_price for item in comparison_items]
        speeds = [item.speed for item in comparison_items]

        price_range = (min(prices), max(prices))
        speed_range = (min(speeds), max(speeds))

        # Определяем лучшие тарифы
        best_for_price = min(comparison_items, key=lambda x: x.effective_price).id
        best_for_speed = max(comparison_items, key=lambda x: x.speed).id
        best_for_value = min(comparison_items, key=lambda x: x.value_score).id
        best_for_features = max(
            comparison_items,
            key=lambda x: (x.has_tv + x.has_phone) * 10 - float(x.connection_cost),
        ).id

        # Генерация практичных рекомендаций
        recommendations = self._generate_recommendations(comparison_items)

        return ComparisonResult(
            tariffs=comparison_items,
            price_range=price_range,
            speed_range=speed_range,
            best_for_price=best_for_price,
            best_for_speed=best_for_speed,
            best_for_value=best_for_value,
            best_for_features=best_for_features,
            price_comparison=price_comparison,
            speed_comparison=speed_comparison,
            feature_comparison=feature_comparison,
            recommendations=recommendations,
        )

    def _calculate_value_score(
        self,
        price: Decimal,
        speed: int,
        has_tv: bool,
        has_phone: bool,
        connection_cost: Decimal,
    ) -> Decimal:
        """Расчет комплексной оценки ценности тарифа"""
        # Базовый score = цена за Мбит/с
        score = price / speed

        # Бонус за дополнительные услуги
        if has_tv:
            score *= Decimal("0.9")  # 10% бонус
        if has_phone:
            score *= Decimal("0.95")  # 5% бонус

        # Штраф за высокую стоимость подключения
        if connection_cost > 0:
            score *= 1 + connection_cost / 10000

        return score

    def _mark_best_tariffs(self, items: list[TariffComparisonItem]) -> None:
        """Маркировка лучших тарифов по разным критериям"""
        if not items:
            return

        # Самый дешевый
        min_price = min(item.effective_price for item in items)
        for item in items:
            if item.effective_price == min_price:
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

        # Лучшие возможности
        max_features_score = max(
            (item.has_tv + item.has_phone) * 10 - float(item.connection_cost)
            for item in items
        )
        for item in items:
            feature_score = (item.has_tv + item.has_phone) * 10 - float(
                item.connection_cost
            )
            if feature_score == max_features_score:
                item.has_best_features = True

    def _create_price_comparison(
        self, items: list[TariffComparisonItem]
    ) -> list[PriceComparison]:
        """Создание детального сравнения по цене"""
        max_price = max(item.effective_price for item in items)

        comparisons = []
        for item in items:
            monthly_savings = (
                max_price - item.effective_price
                if max_price > item.effective_price
                else None
            )

            comparisons.append(
                PriceComparison(
                    tariff_id=item.id,
                    base_price=item.base_price,
                    effective_price=item.effective_price,
                    is_promo=item.is_promo,
                    promo_discount=(
                        item.base_price - item.effective_price
                        if item.is_promo
                        else None
                    ),
                    promo_period=item.promo_period,
                    yearly_cost=item.yearly_cost,
                    monthly_savings=monthly_savings,
                )
            )

        return comparisons

    def _create_speed_comparison(
        self, items: list[TariffComparisonItem]
    ) -> list[SpeedComparison]:
        """Создание детального сравнения по скорости"""
        average_speed = sum(item.speed for item in items) // len(items)
        max_speed = max(item.speed for item in items)

        return [
            SpeedComparison(
                tariff_id=item.id,
                speed=item.speed,
                price_per_mbps=item.price_per_mbps,
                is_fastest=item.speed == max_speed,
                speed_difference=item.speed - average_speed,
            )
            for item in items
        ]

    def _create_feature_comparison(
        self, items: list[TariffComparisonItem]
    ) -> list[FeatureComparison]:
        """Создание детального сравнения по возможностям"""
        comparisons = []

        # Определяем уникальные особенности
        all_have_tv = all(item.has_tv for item in items)
        all_have_phone = all(item.has_phone for item in items)

        for item in items:
            unique_features = []
            if item.has_tv and not all_have_tv:
                unique_features.append("Телевидение")
            if item.has_phone and not all_have_phone:
                unique_features.append("Телефония")
            if item.connection_cost == 0:
                unique_features.append("Бесплатное подключение")

            features_count = sum([item.has_tv, item.has_phone])

            comparisons.append(
                FeatureComparison(
                    tariff_id=item.id,
                    has_tv=item.has_tv,
                    has_phone=item.has_phone,
                    connection_cost=item.connection_cost,
                    features_count=features_count,
                    unique_features=unique_features,
                )
            )

        return comparisons

    def _generate_recommendations(self, items: list[TariffComparisonItem]) -> list[str]:
        """Генерация персонализированных рекомендаций"""
        recommendations = []

        # Находим лучшие тарифы
        cheapest = min(items, key=lambda x: x.effective_price)
        fastest = max(items, key=lambda x: x.speed)
        best_value = min(items, key=lambda x: x.value_score)

        # Практичные рекомендации для выбора
        if cheapest.is_promo:
            recommendations.append(
                f"Тариф '{cheapest.name}' сейчас самый выгодный благодаря акции. "
                f"Экономия составит "
                f"{cheapest.base_price - cheapest.effective_price} ₽/мес "
                f"в течение {cheapest.promo_period} месяцев"
            )
        else:
            recommendations.append(
                f"Тариф '{cheapest.name}' предлагает самую низкую цену - "
                f"{cheapest.effective_price} ₽/мес"
            )

        # Сравнение скорости и цены
        if fastest != cheapest:
            price_diff = fastest.effective_price - cheapest.effective_price
            speed_diff = fastest.speed - cheapest.speed
            recommendations.append(
                f"Тариф '{fastest.name}' стоит на {price_diff} ₽/мес дороже, "
                f"но предоставляет на {speed_diff} Мбит/с больше скорости"
            )

        # Оптимальный выбор
        if best_value not in (cheapest, fastest):
            recommendations.append(
                f"Тариф '{best_value.name}' предлагает оптимальное соотношение цены "
                f"и скорости"
            )

        # Дополнительные услуги
        with_tv = [item for item in items if item.has_tv]
        if with_tv:
            cheapest_with_tv = min(with_tv, key=lambda x: x.effective_price)
            recommendations.append(
                f"Если нужно ТВ, выберите '{cheapest_with_tv.name}' - "
                f"самый доступный тариф с телевидением "
                f"({cheapest_with_tv.effective_price} ₽/мес)"
            )

        # Бесплатное подключение
        free_connection = [item for item in items if item.connection_cost == 0]
        if free_connection and len(free_connection) < len(items):
            recommendations.append(
                f"Обратите внимание: "
                f"тарифы {', '.join(f'«{item.name}»' for item in free_connection)} "
                f"предлагают бесплатное подключение"
            )

        return recommendations
