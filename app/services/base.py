"""BaseService: logika CRUD generik. Subclass cukup mengisi konfigurasi
dan meng-override hook bila ada aturan khusus.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.database import Base
from app.exceptions import NotFoundError, UniqueViolationError
from app.repositories.base import BaseRepository
from app.services.short_id_service import ShortIdService
from app.services.uuid_service import UuidService

ModelT = TypeVar("ModelT", bound=Base)
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)  # wajib punya field `id`


class BaseService(Generic[ModelT, CreateT, UpdateT]):
    # --- konfigurasi subclass ---
    reference_prefix: str = ""
    reference_length: int = 5
    unique_fields: tuple[str, ...] = ()

    def __init__(
        self,
        repo: BaseRepository[ModelT],
        uuid_service: UuidService | None = None,
        short_id_service: ShortIdService | None = None,
    ):
        self.repo = repo
        self.uuid_service = uuid_service or UuidService()
        self.short_id_service = short_id_service or ShortIdService()

    # --- hook yang bisa di-override ---
    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        """Atur default / transformasi data sebelum disimpan."""
        return data

    # --- helper ---
    def _check_unique(self, data: dict[str, Any], exclude_id: str | None = None):
        for field in self.unique_fields:
            if self.repo.exists_by(field, data[field], exclude_id=exclude_id):
                raise UniqueViolationError(field)

    # --- operasi CRUD ---
    def list(self, filtertext: str | None, start: int, length: int) -> dict:
        total = self.repo.count_all()
        rows, filtered = self.repo.search(filtertext, start, length)
        return {"RecordsTotal": total, "RecordsFiltered": filtered, "Data": rows}

    def get_by_reference(self, reference: str) -> ModelT:
        obj = self.repo.find_by_reference(reference)
        if obj is None:
            raise NotFoundError()
        return obj

    def create(self, payload: CreateT) -> ModelT:
        data = self._normalize(payload.model_dump())
        self._check_unique(data)

        obj = self.repo.model(
            id=self.uuid_service.generate(),
            reference=self.short_id_service.generate(
                prefix=self.reference_prefix, length=self.reference_length
            ),
            **data,
        )
        return self.repo.create(obj)

    def update(self, payload: UpdateT) -> ModelT:
        data = self._normalize(payload.model_dump(exclude={"id"}))
        self._check_unique(data, exclude_id=payload.id)

        obj = self.repo.find_by_id(payload.id)
        if obj is None:
            raise NotFoundError()

        for field, value in data.items():
            setattr(obj, field, value)
        return self.repo.save(obj)

    def delete(self, reference: str) -> None:
        self.repo.soft_delete_by_reference(reference)
