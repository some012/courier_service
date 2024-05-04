from pydantic import BaseModel, Field
from typing import Annotated


class BaseSchema(BaseModel):
    id: Annotated[int, Field(gt=0)]
