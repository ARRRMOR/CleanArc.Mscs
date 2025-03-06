from pydantic import BaseModel, conint
from typing import List


class Item(BaseModel):
    item_id: int
    quantity: conint(ge=1)  # quantity >= 1

class OrderDefault(BaseModel):

    items: List[Item]  # список объектов Item
    user_id: int

class ResponseOrder(OrderDefault):
    id: int

    class Config:
        from_attributes = True

