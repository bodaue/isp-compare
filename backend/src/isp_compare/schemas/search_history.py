from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from isp_compare.schemas.tariff import TariffSearchParams


class SearchHistoryCreate(BaseModel):
    search_params: TariffSearchParams


class SearchHistoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    search_params: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
