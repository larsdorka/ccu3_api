from pydantic import BaseModel


class Interface(BaseModel):
    name: str = ""
    port: int = 0
    info: str = ""
