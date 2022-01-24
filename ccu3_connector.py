import requests
import json
import time

from datetime import datetime
from typing import List

from models.WindowStateData import *
from models.JsonRpcRequest import *
from models.Room import *

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
    login_request = LoginRequest()
    login_request.params.username = config_data['ccu3_config']['connection']['username']
    login_request.params.password = config_data['ccu3_config']['connection']['password']
    login_body = str(login_request)
    if _logging:
        print("Request: {0}".format(login_body))
    start_time = time.time()
    response_login = requests.post(config_data['ccu3_config']['connection']['url'], login_body)
    stop_time = time.time()
    duration = (stop_time - start_time) * 1000
    if _logging:
        print("Response: {0}".format(response_login.text))
        print("Duration: {0:.0f} ms".format(duration))
    response_login_object = json.loads(response_login.text)
    _session_id = response_login_object['result']
    return


def rpc_logout():
    global _session_id
    logout_request = LogoutRequest()
    logout_request.params.session_id = _session_id
    logout_body = str(logout_request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(logout_body))
        start_time = time.time()
        response_logout = requests.post(config_data['ccu3_config']['connection']['url'], logout_body)
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
    return


def rpc_getall():
    response_getall_object = None
    getall_request = GetAllRequest()
    getall_request.params.session_id = _session_id
    getall_body = str(getall_request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(getall_body))
        start_time = time.time()
        response_getall = requests.post(config_data['ccu3_config']['connection']['url'], getall_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response_getall.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_getall_object = json.loads(response_getall.text)
    else:
        print("warning: no session")
    return response_getall_object


def get_windowstatedata():
    global windowstate_data
    error_state = False
    error_message = ""
    response_getall_object = rpc_getall()
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
    response_allRooms: List[Room] = []
    getall_request = RoomGetAllRequest()
    getall_request.params.session_id = _session_id
    getall_body = str(getall_request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(getall_body))
        start_time = time.time()
        response_getall = requests.post(config_data['ccu3_config']['connection']['url'], getall_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response_getall.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_getall_object = json.loads(response_getall.text)
        if response_getall_object is not None:
            if response_getall_object['result'] is not None:
                for result in response_getall_object['result']:
                    new_room = Room()
                    new_room.id = result['id']
                    new_room.name = result['name']
                    new_room.description = result['description']
                    for channelId in result['channelIds']:
                        new_room.channelIds.append(channelId)
                    response_allRooms.append(new_room)
    else:
        print("warning: no session")
    return response_allRooms


def rpc_listAllRooms() -> List[str]:
    response_listall_object = None
    listall_request = RoomListAllRequest()
    listall_request.params.session_id = _session_id
    listall_body = str(listall_request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(listall_body))
        start_time = time.time()
        response_listall = requests.post(config_data['ccu3_config']['connection']['url'], listall_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response_listall.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_listall_object = json.loads(response_listall.text)
    else:
        print("warning: no session")
    return response_listall_object['result']


def rpc_getRoom(room_id: str) -> Room:
    response_room: Room = Room()
    getroom_request = RoomGetRequest()
    getroom_request.params.session_id = _session_id
    getroom_request.params.id = room_id
    getroom_body = str(getroom_request)
    if _session_id != "":
        if _logging:
            print("Request: {0}".format(getroom_body))
        start_time = time.time()
        response_getroom = requests.post(config_data['ccu3_config']['connection']['url'], getroom_body)
        stop_time = time.time()
        duration = (stop_time - start_time) * 1000
        if _logging:
            print("Response: {0}".format(response_getroom.text))
            print("Duration: {0:.0f} ms".format(duration))
        response_getroom_object = json.loads(response_getroom.text)
        if response_getroom_object is not None:
            if response_getroom_object['result'] is not None:
                response_room.id = response_getroom_object['result']['id']
                response_room.name = response_getroom_object['result']['name']
                response_room.description = response_getroom_object['result']['description']
                for channelId in response_getroom_object['result']['channelIds']:
                    response_room.channelIds.append(channelId)
    else:
        print("warning: no session")
    return response_room
