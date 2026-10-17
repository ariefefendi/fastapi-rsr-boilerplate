"""BaseRepository: CRUD generik untuk model dengan konvensi kolom:
id (PK string/UUID), reference, created_at, deleted_at (soft delete).
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    # Wajib diisi oleh subclass
    model: type[ModelT]
    # Kolom yang ikut dicari pada global search (LIKE)
    search_fields: tuple[str, ...] = ()

    def __init__(self, db: Session):
        self.db = db

    def _active(self):
        # Padanan SoftDeletes global scope
        return self.model.deleted_at.is_(None)

    # ------------------------------------------------------------- Read
    def count_all(self) -> int:
        return self.db.scalar(
            select(func.count()).select_from(self.model).where(self._active())
        )

    def search(
        self, filtertext: str | None, start: int, length: int
    ) -> tuple[list[ModelT], int]:
        """Return (rows, total_setelah_filter)."""
        stmt = select(self.model).where(self._active())

        if filtertext and self.search_fields:
            like = f"%{filtertext}%"
            stmt = stmt.where(
                or_(*(getattr(self.model, f).like(like) for f in self.search_fields))
            )

        filtered = self.db.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = self.db.scalars(
            stmt.order_by(self.model.created_at.desc()).offset(start).limit(length)
        ).all()
        return list(rows), filtered

    def find_by_id(self, id_: str) -> ModelT | None:
        return self.db.scalars(
            select(self.model).where(self.model.id == id_, self._active())
        ).first()

    def find_by_reference(self, reference: str) -> ModelT | None:
        return self.db.scalars(
            select(self.model).where(
                self.model.reference == reference, self._active()
            )
        ).first()

    def exists_by(self, field: str, value: Any, exclude_id: str | None = None) -> bool:
        """Cek duplikasi kolom. Sengaja TIDAK memfilter soft-deleted
        (sama seperti rule `unique` Laravel)."""
        stmt = select(self.model.id).where(getattr(self.model, field) == value)
        if exclude_id:
            stmt = stmt.where(self.model.id != exclude_id)
        return self.db.scalar(stmt) is not None

    # ------------------------------------------------------------ Write
    def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.commit()
        return obj

    def save(self, obj: ModelT) -> ModelT:
        self.db.commit()
        return obj

    def soft_delete_by_reference(self, reference: str) -> None:
        self.db.execute(
            update(self.model)
            .where(self.model.reference == reference, self._active())
            .values(deleted_at=func.now())
        )
        self.db.commit()
