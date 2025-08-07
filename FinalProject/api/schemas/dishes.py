from typing import Optional
from pydantic import BaseModel


class DishCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price_cents: int
    category_id: int
    is_active: bool = True


class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class DishOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price_cents: int
    category_id: int
    is_active: bool

    class ConfigDict:
        from_attributes = True
