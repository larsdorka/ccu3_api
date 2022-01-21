import requests
import json
import time

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from typing import Optional

login_string = '{"jsonrpc": "1.1", "id": 0, "method": "Session.login", "params": {"username":"", "password":""}}'
logout_string = '{"jsonrpc": "1.1", "id": 0, "method": "Session.logout", "params": {"_session_id_":""}}'
getall_string = '{"jsonrpc": "1.1", "id": 0, "method": "SysVar.getAll", "params": {"_session_id_":""}}'

_session_id = ""
_logging = False

config_data = {}
room_data = {
    "rooms":  []
    }

api = fastapi.FastAPI()

origins = [
    "http://localhost",
    "http://127.0.0.1"
]

api.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=False,
                   allow_methods=["*"],
                   allow_headers=["*"])

api.mount("/WindowState", StaticFiles(directory="WindowState", html=True), name="WindowState")


def load_config(path="config/ccu3_config.json"):
    global config_data, room_data
    try:
        with open(path) as file:
            config_data = json.load(file)
            print("room count: {0}".format(len(config_data['variables'])))
            room_data['rooms'].clear()
            for room_number in range(len(config_data['variables'])):
                new_room = {"name": config_data['variables'][room_number]['name'], "id": config_data['variables'][room_number]['id'], "state": True}
                room_data['rooms'].append(new_room)
    except Exception as ex:
        print("error on reading config file: " + str(ex))
        return False
    return True


def login():
    global _session_id
    login_object = json.loads(login_string)
    login_object['params']['username'] = config_data['username']
    login_object['params']['password'] = config_data['password']
    login_body = json.dumps(login_object)
    if _logging:
        print("Request: {0}".format(login_body))
    start_time = time.time()
    response_login = requests.post(config_data['url'], login_body)
    stop_time = time.time()
    duration = (stop_time - start_time) * 1000
    if _logging:
        print("Response: {0}".format(response_login.text))
        print("Duration: {0:.0f} ms".format(duration))
    response_login_object = json.loads(response_login.text)
    _session_id = response_login_object['result']
    return _session_id


def logout():
    global _session_id
    logout_object = json.loads(logout_string)
    logout_object['params']['_session_id_'] = _session_id
    logout_body = json.dumps(logout_object)
    result = True
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(logout_body))
        start_time = time.time()
        response_logout = requests.post(config_data['url'], logout_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response_logout.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_logout_object = json.loads(response_logout.text)
        result = response_logout_object['result']
        if result:
            _session_id = ""
    else:
        print("warning: no session")
    return result


def get_all():
    response_getall_object = None
    getall_object = json.loads(getall_string)
    getall_object['params']['_session_id_'] = _session_id
    getall_body = json.dumps(getall_object)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(getall_body))
        start_time = time.time()
        response_getall = requests.post(config_data['url'], getall_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Duration: {0:.0f} ms".format(duration))
        response_getall_object = json.loads(response_getall.text)
    else:
        print("warning: no session")
    return response_getall_object


def get_data():
    global room_data
    error_state = False
    error_message = ""
    response_getall_object = get_all()
    if response_getall_object is not None:
        if response_getall_object['result'] is not None:
            for room in room_data['rooms']:
                for result in response_getall_object['result']:
                    if result['id'] == room['id']:
                        room['state'] = (result['value'] == 'true')
                        break
        if response_getall_object['error'] is not None:
            error_state = True
            error_message = response_getall_object['error']['message']
    else:
        error_state = True
    if error_state:
        print(error_message)
    return


@api.get('/')
def index():
    body = "<html>" \
           "<body style='padding: 10px;'>" \
           "<h1>Welcome to the API</h1>" \
           "<div>" \
           "Try it: <a href='/ccu3'>/ccu3</a>" \
           "</div>" \
           "<div>" \
           "Logging: <a href='/ccu3?log=true'>/ccu3?log=true</a>" \
           "</div>" \
           "<div>" \
           "Website: <a href='/WindowState'>/WindowState</a>" \
           "</div>" \
           "</body>" \
           "</html>"

    return fastapi.responses.HTMLResponse(content=body)


@api.get('/ccu3')
def api_get_windowstates(log: Optional[bool] = None):
    global _logging
    if log is not None:
        _logging = log
    else:
        _logging = False
    login()
    get_data()
    logout()
    return room_data


if __name__ == '__main__':
    # initialize and run uvicorn when called as a module
    load_config()
    print(room_data)
    uvicorn.run(api, port=8000, host="0.0.0.0")
else:
    # initialize when called by externally run uvicorn
    load_config()
    print(room_data)
