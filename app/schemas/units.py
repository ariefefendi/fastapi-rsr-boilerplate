from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None  # nullable|boolean


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    id: str = Field(min_length=1, max_length=36)


class UnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reference: str
    code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
