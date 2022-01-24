from pydantic import BaseModel
from typing import List


class Room(BaseModel):
    id: str = ""
    name: str = ""
    description: str = ""
    channelIds: List[str] = []
