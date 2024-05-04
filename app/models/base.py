from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    id = Column(Integer, primary_key=True, index=True, nullable=False)
