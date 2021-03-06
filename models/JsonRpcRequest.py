from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "1.1"
    id: int = 0
    method: str = ""
    params: object = None

    def __str__(self):
        return self.json(by_alias=True)


class NoParams(BaseModel):
    pass


class LoginParams(BaseModel):
    username: str = ""
    password: str = ""


class SessionIdParams(BaseModel):
    session_id: str = Field("", alias="_session_id_")


class SessionIdAndIdParams(BaseModel):
    session_id: str = Field("", alias="_session_id_")
    id: str = ""


class LoginRequest(JsonRpcRequest):
    params: LoginParams = LoginParams()
    method: str = "Session.login"


class LogoutRequest(JsonRpcRequest):
    params: SessionIdParams = SessionIdParams()
    method: str = "Session.logout"


class VariableGetAllRequest(JsonRpcRequest):
    params: SessionIdParams = SessionIdParams()
    method: str = "SysVar.getAll"


# login_string = '{"jsonrpc": "1.1", "id": 0, "method": "Session.login", "params": {"username":"", "password":""}}'
# logout_string = '{"jsonrpc": "1.1", "id": 0, "method": "Session.logout", "params": {"_session_id_":""}}'
# getall_string = '{"jsonrpc": "1.1", "id": 0, "method": "SysVar.getAll", "params": {"_session_id_":""}}'
