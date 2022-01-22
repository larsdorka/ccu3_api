from pydantic import BaseModel
from typing import List
from datetime import datetime


class Room(BaseModel):
    name: str = ""
    id: int = 0
    state: bool = False


class Meta(BaseModel):
    lastUpdated: datetime = None


class RoomData(BaseModel):
    rooms: List[Room] = []
    meta: Meta = Meta()
