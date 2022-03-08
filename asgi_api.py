import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from models.WindowStateData import WindowStateData

import ccu3_connector

api = fastapi.FastAPI()

api.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=False,
                   allow_methods=["*"],
                   allow_headers=["*"])

api.mount("/static", StaticFiles(directory="static", html=True), name="static")


@api.get('/')
def index():
    response = RedirectResponse(url='/static')
    return response


@api.get('/favicon.ico')
def favicon():
    response = RedirectResponse(url='/static/img/favicon.ico')
    return response


@api.get('/api/v1/activate_logging')
def api_activate_logging():
    ccu3_connector._logging = True
    return dict()


@api.get('/api/v1/deactivate_logging')
def api_deactivate_logging():
    ccu3_connector._logging = False
    return dict()


@api.get('/api/v1/ccu3_get_windowstates')
def api_get_windowstates() -> WindowStateData:
    ccu3_connector.rpc_login()
    ccu3_connector.get_windowstatedata()
    ccu3_connector.rpc_logout()
    return ccu3_connector.windowstate_data
