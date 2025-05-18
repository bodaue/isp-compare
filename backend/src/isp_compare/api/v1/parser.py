# backend/src/isp_compare/api/v1/parser.py
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, HTTPException

from isp_compare.api.v1 import security
from isp_compare.schemas.common import APIResponse
from isp_compare.services.identity_provider import IdentityProvider
from isp_compare.services.parser_service import ParserService

router = APIRouter(
    prefix="/parsers", tags=["Parsers"], dependencies=[Depends(security)]
)


@router.post("/run/{provider_name}", dependencies=[Depends(security)])
@inject
async def run_parser(
    provider_name: str,
    service: FromDishka[ParserService],
    identity_provider: FromDishka[IdentityProvider],
) -> APIResponse:
    await identity_provider.ensure_is_admin()

    supported_providers = ["Ростелеком", "Дом.ру", "Билайн"]
    if provider_name not in supported_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый провайдер."
            f" Доступные провайдеры: {', '.join(supported_providers)}",
        )

    count = await service.update_provider_tariffs(provider_name)

    return APIResponse(
        message=f"Успешно обновлено {count} тарифов для провайдера {provider_name}"
    )


@router.post("/run-all", dependencies=[Depends(security)])
@inject
async def run_all_parsers(
    service: FromDishka[ParserService],
    identity_provider: FromDishka[IdentityProvider],
) -> APIResponse:
    await identity_provider.ensure_is_admin()

    results = await service.update_all_tariffs()

    message_parts = []
    for provider_name, count in results.items():
        message_parts.append(f"{provider_name}: {count} тарифов")

    return APIResponse(
        message=f"Результаты обновления тарифов: {', '.join(message_parts)}"
    )
