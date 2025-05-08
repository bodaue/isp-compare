import uuid

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from isp_compare.models.provider import Provider
from isp_compare.models.tariff import ConnectionType, Tariff
from isp_compare.repositories.tariff import TariffRepository


@pytest.fixture
async def tariff_repository(session: AsyncSession) -> TariffRepository:
    return TariffRepository(session=session)


@pytest.fixture
async def test_provider(session: AsyncSession, faker: Faker) -> Provider:
    provider = Provider(
        name=faker.company(),
        description=faker.paragraph(),
        website=faker.url(),
        logo_url=faker.image_url(),
    )
    session.add(provider)
    await session.commit()
    return provider


@pytest.fixture
async def test_tariff(
    session: AsyncSession, test_provider: Provider, faker: Faker
) -> Tariff:
    tariff = Tariff(
        provider_id=test_provider.id,
        name=faker.word() + " Tariff",
        description=faker.paragraph(),
        price=faker.pyfloat(min_value=10, max_value=100, right_digits=2),
        speed=faker.pyint(min_value=50, max_value=1000),
        connection_type=ConnectionType.FTTH,
        has_tv=faker.pybool(),
        has_phone=faker.pybool(),
        additional_services={"vpn": faker.pybool(), "static_ip": faker.pybool()},
        connection_cost=faker.pyfloat(min_value=0, max_value=50, right_digits=2),
        contract_period=faker.pyint(min_value=0, max_value=24),
        is_active=True,
    )
    session.add(tariff)
    await session.commit()
    return tariff


@pytest.fixture
async def test_tariffs(
    session: AsyncSession, test_provider: Provider, faker: Faker
) -> list[Tariff]:
    connection_types = list(ConnectionType)
    tariffs = []

    for i in range(5):
        tariff = Tariff(
            provider_id=test_provider.id,
            name=f"{faker.word()} Tariff {i + 1}",
            description=faker.paragraph(),
            price=faker.pyfloat(min_value=10, max_value=100, right_digits=2),
            speed=faker.pyint(min_value=50, max_value=1000),
            connection_type=connection_types[i % len(connection_types)],
            has_tv=i % 2 == 0,
            has_phone=i % 3 == 0,
            additional_services={"vpn": i % 2 == 0, "static_ip": i % 3 == 0},
            connection_cost=faker.pyfloat(min_value=0, max_value=50, right_digits=2),
            contract_period=None if i % 2 else faker.pyint(min_value=6, max_value=24),
            is_active=True,
        )
        tariffs.append(tariff)
        session.add(tariff)

    inactive_tariff = Tariff(
        provider_id=test_provider.id,
        name=f"{faker.word()} Inactive Tariff",
        description=faker.paragraph(),
        price=faker.pyfloat(min_value=10, max_value=100, right_digits=2),
        speed=faker.pyint(min_value=50, max_value=1000),
        connection_type=ConnectionType.LTE,
        has_tv=False,
        has_phone=False,
        is_active=False,
    )
    tariffs.append(inactive_tariff)
    session.add(inactive_tariff)

    await session.commit()
    return tariffs


async def test_create_tariff(
    session: AsyncSession,
    tariff_repository: TariffRepository,
    test_provider: Provider,
    faker: Faker,
) -> None:
    tariff = Tariff(
        provider_id=test_provider.id,
        name=faker.word() + " Tariff",
        description=faker.paragraph(),
        price=faker.pyfloat(min_value=10, max_value=100, right_digits=2),
        speed=faker.pyint(min_value=50, max_value=1000),
        connection_type=ConnectionType.FTTH,
        has_tv=faker.pybool(),
        has_phone=faker.pybool(),
        additional_services={"vpn": faker.pybool(), "static_ip": faker.pybool()},
        connection_cost=faker.pyfloat(min_value=0, max_value=50, right_digits=2),
        contract_period=faker.pyint(min_value=0, max_value=24),
        is_active=True,
    )

    await tariff_repository.create(tariff)
    await session.flush()

    stmt = select(Tariff).where(Tariff.id == tariff.id)
    result = await session.execute(stmt)
    saved_tariff = result.scalar_one()

    assert saved_tariff.id == tariff.id
    assert saved_tariff.provider_id == test_provider.id
    assert saved_tariff.name == tariff.name
    assert saved_tariff.price == tariff.price
    assert saved_tariff.speed == tariff.speed
    assert saved_tariff.connection_type == tariff.connection_type
    assert saved_tariff.has_tv == tariff.has_tv
    assert saved_tariff.has_phone == tariff.has_phone
    assert saved_tariff.additional_services == tariff.additional_services
    assert saved_tariff.is_active == tariff.is_active


async def test_get_by_id(
    tariff_repository: TariffRepository, test_tariff: Tariff
) -> None:
    result = await tariff_repository.get_by_id(test_tariff.id)

    assert result is not None
    assert result.id == test_tariff.id
    assert result.name == test_tariff.name
    assert result.price == test_tariff.price
    assert result.speed == test_tariff.speed


async def test_get_by_id_for_update(
    tariff_repository: TariffRepository, test_tariff: Tariff
) -> None:
    result = await tariff_repository.get_by_id(test_tariff.id, for_update=True)

    assert result is not None
    assert result.id == test_tariff.id
    assert result.name == test_tariff.name


async def test_get_by_id_not_found(tariff_repository: TariffRepository) -> None:
    non_existent_id = uuid.uuid4()
    result = await tariff_repository.get_by_id(non_existent_id)

    assert result is None


async def test_get_all(
    tariff_repository: TariffRepository, test_tariffs: list[Tariff]
) -> None:
    limit = 10
    offset = 0
    result = await tariff_repository.get_all(limit, offset)

    assert len(result) == len(test_tariffs)

    tariff_ids = {t.id for t in result}
    for tariff in test_tariffs:
        assert tariff.id in tariff_ids


async def test_get_all_with_limit(
    tariff_repository: TariffRepository, test_tariffs: list[Tariff]
) -> None:
    limit = 3
    offset = 0
    result = await tariff_repository.get_all(limit, offset)

    assert len(result) == limit


async def test_get_by_provider(
    tariff_repository: TariffRepository,
    test_provider: Provider,
    test_tariffs: list[Tariff],
) -> None:
    limit = 10
    offset = 0
    result = await tariff_repository.get_by_provider(test_provider.id, limit, offset)

    assert len(result) == len(test_tariffs)

    for tariff in result:
        assert tariff.provider_id == test_provider.id


async def test_get_by_provider_with_limit_offset(
    tariff_repository: TariffRepository,
    test_provider: Provider,
    test_tariffs: list[Tariff],
) -> None:
    limit = 3
    offset = 2
    result = await tariff_repository.get_by_provider(test_provider.id, limit, offset)

    assert len(result) == min(limit, len(test_tariffs) - offset)

    for tariff in result:
        assert tariff.provider_id == test_provider.id


async def test_update(
    session: AsyncSession,
    tariff_repository: TariffRepository,
    test_tariff: Tariff,
    faker: Faker,
) -> None:
    new_name = faker.word() + " Updated"
    new_price = faker.pydecimal(min_value=100, max_value=200, right_digits=2)
    new_speed = faker.pyint(min_value=100, max_value=500)
    update_data = {
        "name": new_name,
        "price": new_price,
        "speed": new_speed,
        "connection_type": ConnectionType.ADSL,
    }

    await tariff_repository.update(test_tariff.id, update_data)
    await session.commit()

    stmt = select(Tariff).where(Tariff.id == test_tariff.id)
    result = await session.execute(stmt)
    updated_tariff = result.scalar_one()

    assert updated_tariff.name == new_name
    assert updated_tariff.price == new_price
    assert updated_tariff.speed == new_speed
    assert updated_tariff.connection_type == ConnectionType.ADSL
    assert updated_tariff.has_tv == test_tariff.has_tv
    assert updated_tariff.provider_id == test_tariff.provider_id


async def test_update_partial(
    session: AsyncSession,
    tariff_repository: TariffRepository,
    test_tariff: Tariff,
    faker: Faker,
) -> None:
    new_name = faker.word() + " Partial Update"
    update_data = {"name": new_name}

    await tariff_repository.update(test_tariff.id, update_data)
    await session.commit()

    stmt = select(Tariff).where(Tariff.id == test_tariff.id)
    result = await session.execute(stmt)
    updated_tariff = result.scalar_one()

    assert updated_tariff.name == new_name
    assert updated_tariff.price == test_tariff.price
    assert updated_tariff.speed == test_tariff.speed
    assert updated_tariff.connection_type == test_tariff.connection_type


async def test_delete(
    session: AsyncSession, tariff_repository: TariffRepository, test_tariff: Tariff
) -> None:
    await tariff_repository.delete(test_tariff)
    await session.commit()

    stmt = select(Tariff).where(Tariff.id == test_tariff.id)
    result = await session.execute(stmt)
    deleted_tariff = result.scalar_one_or_none()

    assert deleted_tariff is None


async def test_search(
    tariff_repository: TariffRepository, test_tariffs: list[Tariff]
) -> None:
    active_tariffs = [t for t in test_tariffs if t.is_active]
    ftth_tariffs = [
        t for t in active_tariffs if t.connection_type == ConnectionType.FTTH
    ]

    result = await tariff_repository.search(
        min_price=None,
        max_price=None,
        min_speed=None,
        max_speed=None,
        connection_type=ConnectionType.FTTH.value,
        has_tv=None,
        has_phone=None,
        limit=10,
        offset=0,
    )

    assert len(result) == len(ftth_tariffs)
    for tariff in result:
        assert tariff.connection_type == ConnectionType.FTTH
        assert tariff.is_active is True


async def test_search_price_range(
    tariff_repository: TariffRepository, test_tariffs: list[Tariff]
) -> None:
    min_price = 30
    max_price = 70

    result = await tariff_repository.search(
        min_price=min_price,
        max_price=max_price,
        min_speed=None,
        max_speed=None,
        connection_type=None,
        has_tv=None,
        has_phone=None,
        limit=10,
        offset=0,
    )

    active_tariffs_in_range = [
        t
        for t in test_tariffs
        if t.is_active and min_price <= float(t.price) <= max_price
    ]

    assert len(result) == len(active_tariffs_in_range)
    for tariff in result:
        assert float(tariff.price) >= min_price
        assert float(tariff.price) <= max_price
        assert tariff.is_active is True


async def test_search_with_tv(
    tariff_repository: TariffRepository, test_tariffs: list[Tariff]
) -> None:
    result = await tariff_repository.search(
        min_price=None,
        max_price=None,
        min_speed=None,
        max_speed=None,
        connection_type=None,
        has_tv=True,
        has_phone=None,
        limit=10,
        offset=0,
    )

    active_tariffs_with_tv = [t for t in test_tariffs if t.is_active and t.has_tv]

    assert len(result) == len(active_tariffs_with_tv)
    for tariff in result:
        assert tariff.has_tv is True
        assert tariff.is_active is True


async def test_search_complex(
    tariff_repository: TariffRepository, test_tariffs: list[Tariff]
) -> None:
    min_speed = 100
    has_phone = True

    result = await tariff_repository.search(
        min_price=None,
        max_price=None,
        min_speed=min_speed,
        max_speed=None,
        connection_type=None,
        has_tv=None,
        has_phone=has_phone,
        limit=10,
        offset=0,
    )

    matching_tariffs = [
        t
        for t in test_tariffs
        if t.is_active and t.speed >= min_speed and t.has_phone == has_phone
    ]

    assert len(result) == len(matching_tariffs)
    for tariff in result:
        assert tariff.speed >= min_speed
        assert tariff.has_phone is True
        assert tariff.is_active is True


async def test_search_limit_offset(
    tariff_repository: TariffRepository, test_tariffs: list[Tariff]
) -> None:
    limit = 2
    offset = 1

    result = await tariff_repository.search(
        min_price=None,
        max_price=None,
        min_speed=None,
        max_speed=None,
        connection_type=None,
        has_tv=None,
        has_phone=None,
        limit=limit,
        offset=offset,
    )

    active_tariffs = [t for t in test_tariffs if t.is_active]
    expected_count = min(limit, len(active_tariffs) - offset)

    assert len(result) == expected_count
    assert result[0].id == active_tariffs[offset].id
