import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
import json
from typing import Optional, List

from models.WindowStateData import WindowStateData
from models.Room import Room
import ccu3_connector


api = fastapi.FastAPI()

api.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=False,
                   allow_methods=["*"],
                   allow_headers=["*"])

api.mount("/WindowState", StaticFiles(directory="WindowState", html=True), name="WindowState")


@api.get('/')
def index():
    response = RedirectResponse(url='/WindowState')
    return response


@api.get('/favicon.ico')
def favicon():
    response = RedirectResponse(url='/WindowState/favicon.ico')
    return response


@api.get('/api/v1/ccu3_get_windowstates')
def api_get_windowstates(log: Optional[bool] = None) -> WindowStateData:
    if log is not None:
        ccu3_connector._logging = log
    else:
        ccu3_connector._logging = False
    ccu3_connector.rpc_login()
    ccu3_connector.get_windowstatedata()
    ccu3_connector.rpc_logout()
    return ccu3_connector.windowstate_data


@api.get('/api/v1/ccu3_get_allrooms')
def api_get_allrooms() -> List[Room]:
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_getAllRooms()
    ccu3_connector.rpc_logout()
    return response


@api.get('/api/v1/ccu3_list_allrooms')
def api_list_allrooms() -> List[str]:
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_listAllRooms()
    ccu3_connector.rpc_logout()
    return response


@api.get('/api/v1/ccu3_get_room')
def api_get_room(room_id: str) -> Room:
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_getRoom(room_id)
    ccu3_connector.rpc_logout()
    return response


if __name__ == '__main__':
    # development mode, local hosting only
    # initialize and run uvicorn when called as a module
    ccu3_connector.load_config()
    uvicorn.run("main:api", port=8000, host="127.0.0.1", reload=True)
else:
    # production mode
    # initialize when called by externally run uvicorn
    ccu3_connector.load_config()
