from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "1.1"
    id: int = 0
    method: str = ""
    params: object = None

    def __str__(self):
        return self.json(by_alias=True)


class LoginParams(BaseModel):
    username: str = ""
    password: str = ""


class LogoutParams(BaseModel):
    session_id: str = Field("", alias="_session_id_")


class GetallParams(BaseModel):
    session_id: str = Field("", alias="_session_id_")


class LoginRequest(JsonRpcRequest):
    params: LoginParams = LoginParams()
    method: str = "Session.login"


class LogoutRequest(JsonRpcRequest):
    params: LogoutParams = LogoutParams()
    method: str = "Session.logout"


class GetallRequest(JsonRpcRequest):
    params: GetallParams = GetallParams()
    method: str = "SysVar.getAll"


# login_string = '{"jsonrpc": "1.1", "id": 0, "method": "Session.login", "params": {"username":"", "password":""}}'
# logout_string = '{"jsonrpc": "1.1", "id": 0, "method": "Session.logout", "params": {"_session_id_":""}}'
# getall_string = '{"jsonrpc": "1.1", "id": 0, "method": "SysVar.getAll", "params": {"_session_id_":""}}'
