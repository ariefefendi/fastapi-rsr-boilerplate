from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class DataTableResponse(BaseModel, Generic[T]):
    """Response datatable server-side, dipakai semua modul:
    response_model=DataTableResponse[UnitOut]
    """

    RecordsTotal: int
    RecordsFiltered: int
    Data: list[T]
