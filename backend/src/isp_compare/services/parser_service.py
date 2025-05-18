import logging
from typing import TYPE_CHECKING

from isp_compare.models.tariff import Tariff
from isp_compare.parsers.beeline import BeelineParser
from isp_compare.parsers.domru import DomruParser
from isp_compare.parsers.rostelecom import RostelecomParser
from isp_compare.repositories.provider import ProviderRepository
from isp_compare.repositories.tariff import TariffRepository
from isp_compare.schemas.tariff import TariffCreate
from isp_compare.services.transaction_manager import TransactionManager

if TYPE_CHECKING:
    from isp_compare.parsers.base import BaseParser

logger = logging.getLogger(__name__)


class ParserService:
    def __init__(
        self,
        provider_repository: ProviderRepository,
        tariff_repository: TariffRepository,
        transaction_manager: TransactionManager,
    ) -> None:
        self._provider_repository = provider_repository
        self._tariff_repository = tariff_repository
        self._transaction_manager = transaction_manager

        self._parsers: dict[str, type[BaseParser]] = {
            "Ростелеком": RostelecomParser,
            "Дом.ру": DomruParser,
            "Билайн": BeelineParser,
        }

    async def parse_provider_tariffs(self, provider_name: str) -> list[TariffCreate]:
        if provider_name not in self._parsers:
            logger.error(f"Parser for provider '{provider_name}' not found")
            return []

        parser_class = self._parsers[provider_name]
        parser = parser_class()

        try:
            providers_with_counts = await self._provider_repository.get_all()
            for provider, _ in providers_with_counts:
                if provider.name == provider_name:
                    parser.provider_id = provider.id
                    break

            if not parser.provider_id:
                logger.error(f"Provider '{provider_name}' not found in database")
                return []

            tariffs = await parser.parse_tariffs()
            logger.info(
                f"Successfully parsed {len(tariffs)} tariffs for {provider_name}"
            )

        except Exception as e:
            logger.exception(f"Error parsing tariffs for {provider_name}: {e!s}")
            return []
        else:
            return tariffs

    async def update_provider_tariffs(self, provider_name: str) -> int:
        tariffs = await self.parse_provider_tariffs(provider_name)
        if not tariffs:
            return 0

        parser = self._parsers[provider_name]()
        provider_id = parser.provider_id

        count = 0
        for tariff_data in tariffs:
            try:
                tariff = Tariff(**tariff_data.model_dump(), provider_id=provider_id)
                await self._tariff_repository.create(tariff)
                count += 1

            except Exception as e:
                logger.exception(f"Error saving tariff {tariff_data.name}: {e!s}")
                continue

        await self._transaction_manager.commit()
        logger.info(f"Updated {count} tariffs for {provider_name}")
        return count

    async def update_all_tariffs(self) -> dict[str, int]:
        results = {}

        for provider_name in self._parsers:
            count = await self.update_provider_tariffs(provider_name)
            results[provider_name] = count

        return results
