from typing import Any

from app.models.units import Units
from app.schemas.units import UnitCreate, UnitUpdate
from app.services.base import BaseService


class UnitsService(BaseService[Units, UnitCreate, UnitUpdate]):
    reference_prefix = "UN"
    reference_length = 5
    unique_fields = ("code",)

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        # nullable|boolean, default aktif (is_active ?? 1)
        if data.get("is_active") is None:
            data["is_active"] = True
        return data
