import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
from typing import Optional

from room_data import RoomData
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
def api_get_windowstates(log: Optional[bool] = None) -> RoomData:
    if log is not None:
        ccu3_connector._logging = log
    else:
        ccu3_connector._logging = False
    ccu3_connector.login()
    ccu3_connector.get_data()
    ccu3_connector.logout()
    return ccu3_connector.room_data


if __name__ == '__main__':
    # development mode, local hosting only
    # initialize and run uvicorn when called as a module
    ccu3_connector.load_config()
    print(ccu3_connector.room_data)
    uvicorn.run(api, port=8000, host="127.0.0.1")
else:
    # production mode
    # initialize when called by externally run uvicorn
    ccu3_connector.load_config()
