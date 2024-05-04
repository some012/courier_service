from datetime import datetime

from pydantic import Field, BaseModel
from typing import Annotated
from app.schemas.base import BaseSchema


class Orders(BaseSchema):
    name: Annotated[str, Field(min_length=2, max_length=30)]
    courier_id: Annotated[int, Field(ge=0)]
    status: Annotated[int, Field(gt=0)]
    district: Annotated[str, Field(min_length=2, max_length=30)]
    date_get: datetime
    date_end: datetime

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "1",
                "name": "Машина",
                "courier_id": "2",
                "status": "1",
                "district": "district1"
            }
        }


class CreateOrders(BaseSchema):
    id: None = None
    name: Annotated[str, Field(min_length=2, max_length=30)]
    district: Annotated[str, Field(min_length=2, max_length=30)]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Car",
                "district": "district1"
            }
        }


class GetOrdersFinish(BaseModel):
    id: Annotated[int, Field(ge=0)]
    courier_id: Annotated[int, Field(ge=0)]
    status: Annotated[int, Field(gt=0)]
    district: Annotated[str, Field(min_length=2, max_length=30)]
    date_get: datetime
    date_end: datetime


class GetOrdersNotFinish(BaseModel):
    id: Annotated[int, Field(ge=0)]
    courier_id: Annotated[int, Field(ge=0)]
    status: Annotated[int, Field(gt=0)]
    district: Annotated[str, Field(min_length=2, max_length=30)]
    date_get: datetime
