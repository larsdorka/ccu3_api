import requests
import json
import time

from datetime import datetime
from typing import List

from models.JsonRpcRequest import *
from models.WindowStateData import WindowStateData, RoomState
from models.Room import Room
from models.Program import Program
from models.Interface import Interface

_session_id = ""
_logging = False

config_data = {}
windowstate_data = WindowStateData()


def load_config(path="config/config.json"):
    global config_data, windowstate_data
    try:
        with open(path) as file:
            config_data = json.load(file)
            print("room count: {0}".format(len(config_data['ccu3_config']['variables'])))
            windowstate_data.rooms.clear()
            for room_number in range(len(config_data['ccu3_config']['variables'])):
                new_room = RoomState(name=config_data['ccu3_config']['variables'][room_number]['name'], id=config_data['ccu3_config']['variables'][room_number]['id'], state=False)
                windowstate_data.rooms.append(new_room)
    except Exception as ex:
        print("error on reading config file: " + str(ex))
        return False
    return


def rpc_login():
    global _session_id
    request = LoginRequest()
    request.params.username = config_data['ccu3_config']['connection']['username']
    request.params.password = config_data['ccu3_config']['connection']['password']
    request_body = str(request)
    if _logging:
        print("Request: {0}".format(request_body))
    start_time = time.time()
    response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
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
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
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
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
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


def rpc_getAllRooms() -> List[Room]:
    result_object: List[Room] = []
    request = RoomGetAllRequest()
    request.params.session_id = _session_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_object = json.loads(response.text)
        if response_object is not None:
            if response_object['result'] is not None:
                for result in response_object['result']:
                    new_room = Room()
                    new_room.id = result['id']
                    new_room.name = result['name']
                    new_room.description = result['description']
                    for channelId in result['channelIds']:
                        new_room.channelIds.append(channelId)
                    result_object.append(new_room)
    else:
        print("warning: no session")
    return result_object


def rpc_listAllRooms() -> List[str]:
    result_object = None
    request = RoomListAllRequest()
    request.params.session_id = _session_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        result_object = json.loads(response.text)['result']
    else:
        print("warning: no session")
    return result_object


def rpc_getRoom(room_id: str) -> Room:
    result_object: Room = Room()
    request = RoomGetRequest()
    request.params.session_id = _session_id
    request.params.id = room_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_object = json.loads(response.text)
        if response_object is not None:
            if response_object['result'] is not None:
                result_object.id = response_object['result']['id']
                result_object.name = response_object['result']['name']
                result_object.description = response_object['result']['description']
                for channelId in response_object['result']['channelIds']:
                    result_object.channelIds.append(channelId)
    else:
        print("warning: no session")
    return result_object


def rpc_getAllPrograms() -> List[Program]:
    result_object: List[Program] = []
    request = ProgramGetAllRequest()
    request.params.session_id = _session_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_object = json.loads(response.text)
        if response_object is not None:
            if response_object['result'] is not None:
                for result in response_object['result']:
                    new_program = Program()
                    new_program.id = result['id']
                    new_program.name = result['name']
                    new_program.isActive = result['isActive']
                    new_program.isInternal = result['isInternal']
                    new_program.lastExecuteTime = result['lastExecuteTime']
                    result_object.append(new_program)
    else:
        print("warning: no session")
    return result_object


def rpc_listAllDevices() -> List[str]:
    result_object = None
    request = DeviceListAllRequest()
    request.params.session_id = _session_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        result_object = json.loads(response.text)['result']
    else:
        print("warning: no session")
    return result_object


def rpc_getDevice(device_id: str):
    result_object: None
    request = DeviceGetRequest()
    request.params.session_id = _session_id
    request.params.id = device_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_object = json.loads(response.text)
        result_object = response_object
    else:
        print("warning: no session")
    return result_object


def rpc_listAllInterfaces() -> List[Interface]:
    result_object: List[Interface] = []
    request = InterfaceListAllRequest()
    request.params.session_id = _session_id
    request_body = str(request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(request_body))
        start_time = time.time()
        response = requests.post(config_data['ccu3_config']['connection']['url'], request_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_object = json.loads(response.text)
        if response_object is not None:
            if response_object['result'] is not None:
                for result in response_object['result']:
                    new_interface = Interface()
                    new_interface.name = result['name']
                    new_interface.port = result['port']
                    new_interface.info = result['info']
                    result_object.append(new_interface)
    else:
        print("warning: no session")
    return result_object
