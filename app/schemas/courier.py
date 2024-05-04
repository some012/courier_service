from datetime import datetime
from typing import List
from pydantic import Field, BaseModel
from typing import Annotated, Optional
from app.schemas.base import BaseSchema


class Courier(BaseSchema):
    name: Annotated[str, Field(min_length=2, max_length=30)]
    avg_order_complete_time: datetime
    avg_day_orders: Annotated[int, Field(ge=0)]
    active_order_id: Annotated[int, Field(ge=0)]
    active_order: Optional[dict]

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "name": "Mikhail",
                "avg_order_complete_time": "2024-01-08 12:15:02",
                "avg_day_orders": "24"
            }
        }


class CreateCourier(BaseSchema):  # создаем нового курьера с помощью name и districts
    id: None = None
    name: Annotated[str, Field(min_length=2, max_length=30)]
    districts: List[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Mikhail",
                "districts": ["district1", "district2"]
            }
        }


class GetAllCourier(BaseModel):  # выводим у всех курьеров только id, name и districts
    id: Annotated[int, Field(ge=0)]
    name: Annotated[str, Field(min_length=2, max_length=30)]
    districts: Annotated[str, Field(min_length=2, max_length=50)]


class GetWithoutOrderCourier(BaseModel):  # вывод информации без активного заказа со средними значениями
    id: Annotated[int, Field(ge=0)]
    name: Annotated[str, Field(min_length=2, max_length=30)]
    avg_order_complete_time: float
    avg_day_orders: Annotated[int, Field(ge=0)]


class GetWithOrderCourier(BaseModel):  # вывод информации вместе с активным заказом
    id: Annotated[int, Field(ge=0)]
    name: Annotated[str, Field(min_length=2, max_length=30)]
    active_order: Optional[dict]
