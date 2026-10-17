"""Router: hanya urusan HTTP (parse request -> panggil service -> response)."""

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_user
from app.dependencies.units import get_units_service
from app.schemas.common import DataTableResponse
from app.schemas.units import UnitCreate, UnitOut, UnitUpdate
from app.services.units_service import UnitsService

router = APIRouter(
    prefix="/master-data/units",
    tags=["Master Data - Units"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=DataTableResponse[UnitOut])
def get_data_all(
    filtertext: str | None = Query(None),
    start: int = Query(0, ge=0),
    length: int = Query(10, ge=1),
    service: UnitsService = Depends(get_units_service),
):
    return service.list(filtertext, start, length)


@router.get("/select", response_model=UnitOut)
def get_data_select(
    reference: str = Query(...),
    service: UnitsService = Depends(get_units_service),
):
    return service.get_by_reference(reference)


@router.post("")
def insert(payload: UnitCreate, service: UnitsService = Depends(get_units_service)):
    service.create(payload)
    return {"result": "OK"}


@router.put("")
def update_unit(
    payload: UnitUpdate, service: UnitsService = Depends(get_units_service)
):
    service.update(payload)
    return {"result": "OK"}


@router.delete("")
def destroy(
    reference: str = Query(...),
    service: UnitsService = Depends(get_units_service),
):
    service.delete(reference)
    return {"result": "OK"}
