from pydantic import BaseModel
from typing import List


class Room(BaseModel):
    name: str = ""
    id: int = 0
    state: bool = False


class RoomData(BaseModel):
    rooms: List[Room] = []
