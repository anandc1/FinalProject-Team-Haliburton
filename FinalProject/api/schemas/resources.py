from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ResourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    amount: int
    unit: str = "units"
    is_active: bool = True


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class ResourceOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    amount: int
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True


class Resource(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    amount: int
    unit: str
    is_active: bool

    class ConfigDict:
        from_attributes = True
