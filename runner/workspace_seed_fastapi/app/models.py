from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str = ""
    quantity: int = 0
    price: float = 0.0


class Item(ItemCreate):
    id: int
