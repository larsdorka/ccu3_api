from pydantic import BaseModel


class Program(BaseModel):
    id: str = ""
    name: str = ""
    isActive: bool = False
    isInternal: bool = False
    lastExecuteTime: str = ""
