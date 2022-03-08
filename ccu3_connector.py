import requests
import json
import time

from datetime import datetime

from models.JsonRpcRequest import *
from models.WindowStateData import WindowStateData, RoomState

_session_id = ""
_logging = False

ccu3_config_data: dict = {}
windowstate_data: WindowStateData = WindowStateData()


def initialize(ccu3_config: dict):
    global ccu3_config_data, windowstate_data
    ccu3_config_data = ccu3_config
    windowstate_data.rooms.clear()
    for room_number in range(len(ccu3_config_data['variables'])):
        new_room = RoomState(name=ccu3_config_data['variables'][room_number]['name'], id=ccu3_config_data['variables'][room_number]['id'], state=False)
        windowstate_data.rooms.append(new_room)
    print("")
    print("ccu3_connector initialized")
    print("room count: {0}".format(len(windowstate_data.rooms)))
    return


def rpc_login():
    global _session_id
    request = LoginRequest()
    request.params.username = ccu3_config_data['connection']['username']
    request.params.password = ccu3_config_data['connection']['password']
    request_body = str(request)
    if _logging:
        print("Request: {0}".format(request_body))
    start_time = time.time()
    response = requests.post(ccu3_config_data['connection']['url'], request_body)
    stop_time = time.time()
    duration = (stop_time - start_time) * 1000
    if _logging:
        print("Response: {0}".format(response.text))
        print("Duration: {0:.0f} ms".format(duration))
    response_object = json.loads(response.text)
    _session_id = response_object['result']
    return


def rpc_logout():
    global _session_id
    request = LogoutRequest()
    request.params.session_id = _session_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(ccu3_config_data['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_object = json.loads(response.text)
        result = response_object['result']
        if result:
            _session_id = ""
    else:
        print("warning: no session")
    return


def rpc_getAllVariables():
    result_object = None
    request = VariableGetAllRequest()
    request.params.session_id = _session_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(ccu3_config_data['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        result_object = json.loads(response.text)
    else:
        print("warning: no session")
    return result_object


def get_windowstatedata():
    global windowstate_data
    error_state = False
    error_message = ""
    response_getall_object = rpc_getAllVariables()
    if response_getall_object is not None:
        if response_getall_object['result'] is not None:
            for room in windowstate_data.rooms:
                for result in response_getall_object['result']:
                    if int(result['id']) == room.id:
                        room.state = (result['value'] == 'true')
                        break
            windowstate_data.meta.lastUpdated = datetime.now()
        if response_getall_object['error'] is not None:
            error_state = True
            error_message = response_getall_object['error']['message']
    else:
        error_state = True
    if error_state:
        print(error_message)
    return
