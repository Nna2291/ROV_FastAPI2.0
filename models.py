from typing import Optional

from pydantic import BaseModel


class Engine(BaseModel):
    id1: int
    id2: Optional[int]


class EngineOn(Engine):
    speed: float
    reverse1: Optional[bool] = False
    reverse2: Optional[bool] = False
