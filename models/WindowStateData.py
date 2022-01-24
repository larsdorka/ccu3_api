from pydantic import BaseModel
from typing import List
from datetime import datetime


class RoomState(BaseModel):
    name: str = ""
    id: int = 0
    state: bool = False


class Meta(BaseModel):
    lastUpdated: datetime = None


class WindowStateData(BaseModel):
    rooms: List[RoomState] = []
    meta: Meta = Meta()
