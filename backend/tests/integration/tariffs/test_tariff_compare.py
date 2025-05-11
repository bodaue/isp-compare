import uuid

from httpx import AsyncClient

from isp_compare.models import Provider
from isp_compare.models.tariff import Tariff
from tests.utils import check_response


async def test_compare_tariffs_success(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест успешного сравнения тарифов"""
    # Берем первые 3 тарифа для сравнения
    comparison_data = {"tariff_ids": [str(tariff.id) for tariff in tariffs[:3]]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    # Проверяем структуру ответа
    assert "items" in data
    assert "recommendations" in data
    assert "summary" in data

    # Проверяем количество элементов
    assert len(data["items"]) == 3

    # Проверяем поля каждого элемента
    for item in data["items"]:
        assert "id" in item
        assert "name" in item
        assert "provider_name" in item
        assert "current_price" in item
        assert "original_price" in item
        assert "is_promo" in item
        assert "speed" in item
        assert "features" in item
        assert "connection_cost" in item
        assert "price_per_mbps" in item
        assert "yearly_cost" in item
        assert "value_score" in item
        assert "is_cheapest" in item
        assert "is_fastest" in item
        assert "is_best_value" in item
        assert "has_most_features" in item

    # Проверяем, что есть рекомендации
    assert len(data["recommendations"]) > 0
    assert isinstance(data["summary"], str)
    assert len(data["summary"]) > 0


async def test_compare_tariffs_minimum_count(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест сравнения минимального количества тарифов (2)"""
    comparison_data = {"tariff_ids": [str(tariff.id) for tariff in tariffs[:2]]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    assert len(data["items"]) == 2
    assert len(data["recommendations"]) > 0


async def test_compare_tariffs_maximum_count(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест сравнения максимального количества тарифов (5)"""
    comparison_data = {"tariff_ids": [str(tariff.id) for tariff in tariffs[:5]]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    assert len(data["items"]) == 5
    assert len(data["recommendations"]) > 0


async def test_compare_tariffs_too_few(client: AsyncClient, tariff: Tariff) -> None:
    """Тест с слишком малым количеством тарифов"""
    comparison_data = {"tariff_ids": [str(tariff.id)]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    check_response(response, 422)


async def test_compare_tariffs_too_many(
    client: AsyncClient, tariffs: list[Tariff], provider: Provider
) -> None:
    """Тест с слишком большим количеством тарифов"""
    # Создаем дополнительный тариф, чтобы было 6
    extra_tariff = Tariff(
        provider_id=provider.id,
        name="Extra Tariff",
        description="Extra tariff for testing",
        price=99.99,
        speed=1000,
        has_tv=True,
        has_phone=True,
        connection_cost=0,
        is_active=True,
    )

    tariff_ids = [str(t.id) for t in tariffs] + [str(extra_tariff.id)]
    comparison_data = {
        "tariff_ids": tariff_ids[:6]  # Берем 6 тарифов
    }

    response = await client.post("/tariffs/comparison", json=comparison_data)
    check_response(response, 422)


async def test_compare_tariffs_nonexistent(client: AsyncClient, tariff: Tariff) -> None:
    """Тест с несуществующим тарифом"""
    nonexistent_id = str(uuid.uuid4())
    comparison_data = {"tariff_ids": [str(tariff.id), nonexistent_id]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    check_response(response, 404)


async def test_compare_tariffs_duplicate_ids(
    client: AsyncClient, tariff: Tariff, tariffs: list[Tariff]
) -> None:
    """Тест с дублирующимися ID тарифов"""
    # Отправляем один и тот же ID дважды
    comparison_data = {
        "tariff_ids": [str(tariff.id), str(tariff.id), str(tariffs[0].id)]
    }

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    # Должны быть удалены дубликаты
    assert len(data["items"]) == 2
    unique_ids = {item["id"] for item in data["items"]}
    assert len(unique_ids) == 2


async def test_compare_tariffs_with_promo(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест сравнения тарифов с акциями"""
    # Выбираем тарифы с акциями (из фикстуры tariffs с четными индексами есть promo)
    promo_tariffs = [t for t in tariffs if t.promo_price is not None][:2]
    comparison_data = {"tariff_ids": [str(t.id) for t in promo_tariffs]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    # Проверяем, что акционные тарифы правильно обработаны
    for item in data["items"]:
        if item["is_promo"]:
            assert float(item["current_price"]) < float(item["original_price"])
            assert item["promo_period"] is not None


async def test_compare_tariffs_best_markers(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест правильности маркировки лучших тарифов"""
    comparison_data = {"tariff_ids": [str(tariff.id) for tariff in tariffs[:4]]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    # Должен быть хотя бы один самый дешевый
    cheapest_count = sum(1 for item in data["items"] if item["is_cheapest"])
    assert cheapest_count >= 1

    # Должен быть хотя бы один самый быстрый
    fastest_count = sum(1 for item in data["items"] if item["is_fastest"])
    assert fastest_count >= 1

    # Должен быть хотя бы один с лучшим соотношением цена/качество
    best_value_count = sum(1 for item in data["items"] if item["is_best_value"])
    assert best_value_count >= 1


async def test_compare_tariffs_inactive(
    client: AsyncClient, tariff: Tariff, inactive_tariff: Tariff
) -> None:
    """Тест сравнения с неактивным тарифом"""
    comparison_data = {"tariff_ids": [str(tariff.id), str(inactive_tariff.id)]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    check_response(response, 404)


async def test_compare_tariffs_recommendations(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест генерации рекомендаций"""
    comparison_data = {"tariff_ids": [str(tariff.id) for tariff in tariffs[:3]]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    recommendations = data["recommendations"]
    assert len(recommendations) > 0

    # Проверяем, что рекомендации содержат осмысленный текст
    for recommendation in recommendations:
        assert isinstance(recommendation, str)
        assert len(recommendation) > 10  # Минимальная длина рекомендации

    # Проверяем, что хотя бы некоторые рекомендации содержат конкретные данные
    has_price = any("₽" in rec for rec in recommendations)
    has_speed = any("Мбит/с" in rec for rec in recommendations)
    assert has_price or has_speed

    # Проверяем, что есть ключевые типы рекомендаций
    recommendation_text = " ".join(recommendations)
    key_phrases = [
        "Самый доступный",
        "Самый быстрый",
        "Оптимальный выбор",
        "Лучшая акция",
        "С телевидением",
    ]
    # Хотя бы одна из ключевых фраз должна присутствовать
    assert any(phrase in recommendation_text for phrase in key_phrases)


async def test_compare_tariffs_features(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест сравнения тарифов с разными услугами"""
    # Выбираем тарифы с разными услугами
    with_tv = next(t for t in tariffs if t.has_tv)
    with_phone = next(t for t in tariffs if t.has_phone)

    comparison_data = {"tariff_ids": [str(with_tv.id), str(with_phone.id)]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    # Проверяем, что features правильно отображаются
    items = data["items"]
    tv_item = next(item for item in items if item["id"] == str(with_tv.id))
    phone_item = next(item for item in items if item["id"] == str(with_phone.id))

    assert "ТВ" in tv_item["features"]
    assert "Телефон" in phone_item["features"]


async def test_compare_tariffs_value_calculation(
    client: AsyncClient, tariffs: list[Tariff]
) -> None:
    """Тест расчета показателей ценности"""
    comparison_data = {"tariff_ids": [str(tariff.id) for tariff in tariffs[:2]]}

    response = await client.post("/tariffs/comparison", json=comparison_data)
    data = check_response(response, 200)

    for item in data["items"]:
        # Проверяем правильность расчета price_per_mbps
        expected_price_per_mbps = float(item["current_price"]) / item["speed"]
        assert abs(float(item["price_per_mbps"]) - expected_price_per_mbps) < 0.01

        # Проверяем правильность расчета yearly_cost
        expected_yearly_cost = float(item["current_price"]) * 12
        assert abs(float(item["yearly_cost"]) - expected_yearly_cost) < 0.01

        # Проверяем, что value_score рассчитан
        assert float(item["value_score"]) > 0
