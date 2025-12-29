from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None


class ItemInDB(ItemBase):
    id: int

    class Config:
        from_attributes = True
