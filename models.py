from typing import Optional

from pydantic import BaseModel


class Engine(BaseModel):
    id: int


class EngineOn(Engine):
    speed: float
    reverse: Optional[bool] = False
