from datetime import datetime
from typing import Annotated

from pydantic import Field

from app.schemas.base import BaseSchema


class Orders_Backup(BaseSchema):
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