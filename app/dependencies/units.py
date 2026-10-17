"""Wiring dependency: Session -> Repository -> Service."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.units_repository import UnitsRepository
from app.services.units_service import UnitsService


def get_units_repository(db: Session = Depends(get_db)) -> UnitsRepository:
    return UnitsRepository(db)


def get_units_service(
    repo: UnitsRepository = Depends(get_units_repository),
) -> UnitsService:
    return UnitsService(repo)
