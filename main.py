import sys
import os
import contextlib
import time

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
from typing import List

from models.WindowStateData import WindowStateData
from models.Room import Room
from models.Program import Program
from models.Interface import Interface

import threading

import ccu3_connector


class BackgroundServer(uvicorn.Server):
    def install_signal_handlers(self) -> None:
        pass
        return

    @contextlib.contextmanager
    def run_in_thread(self) -> None:
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()
        return


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


@api.get('/api/v1/ccu3_get_allprograms')
def api_get_allprograms() -> List[Program]:
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_getAllPrograms()
    ccu3_connector.rpc_logout()
    return response


@api.get('/api/v1/ccu3_list_alldevices')
def api_list_alldevices() -> List[str]:
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_listAllDevices()
    ccu3_connector.rpc_logout()
    return response


@api.get('/api/v1/ccu3_get_device')
def api_get_device(device_id: str) -> Room:
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_getDevice(device_id)
    ccu3_connector.rpc_logout()
    return response


@api.get('/api/v1/ccu3_list_allinterfaces')
def api_list_allinterfaces() -> List[Interface]:
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_listAllInterfaces()
    ccu3_connector.rpc_logout()
    return response


@api.get('/api/v1/ccu3_get_value_from_channel')
def api_get_value_from_channel(channel_id: str):
    ccu3_connector.rpc_login()
    response = ccu3_connector.rpc_getDevice(channel_id)
    ccu3_connector.rpc_logout()
    return response


if __name__ == '__main__':
    logpath = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(logpath):
        os.mkdir(logpath)
    file_stdout = open(os.path.join(logpath, "stdout.log"), "a")
    sys.stdout = file_stdout
    sys.stderr = file_stdout

    ccu3_connector.load_config()

    print("starting...")
    uvi_config = uvicorn.Config(api, port=8000, host="0.0.0.0")
    uvi_server = BackgroundServer(config=uvi_config)
    with uvi_server.run_in_thread():
        time.sleep(1)
        print("started")
        try:
            x = input("press any key")
        except KeyboardInterrupt:
            pass
        print("stopping...")
    print("stopped")

    file_stdout.close()
