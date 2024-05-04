from pydantic import Field, BaseModel
from typing import Annotated
from app.schemas.base import BaseSchema


class Orders(BaseSchema):
    name: Annotated[str, Field(min_length=2, max_length=30)]
    courier_id: Annotated[int, Field(gt=0)]
    status: Annotated[int, Field(gt=0)]
    district: Annotated[str, Field(min_length=2, max_length=30)]

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


class GetOrders(BaseModel):  # get выводит только эти две переменные
    courier_id: Annotated[int, Field(allow_none=True)]
    status: Annotated[int, Field(gt=0)]
