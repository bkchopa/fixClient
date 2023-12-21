import json
import os
import requests
from typing import Tuple
import winreg

LCU_URL = None
HEADERS = None
AUTH = None
def get_lol_client_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\FixBot') as key:
            return winreg.QueryValueEx(key, 'LoLPath')[0]
    except FileNotFoundError:
        return None

def set_lcu_globals(url, headers, auth):
    global LCU_URL, HEADERS, AUTH
    LCU_URL = url
    HEADERS = headers
    AUTH = auth

def find_lockfile_path():
    # 검색할 드라이브 목록
    drives = ['C:', 'D:', 'E:']

    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if 'lockfile' in files:
                return os.path.join(root, 'lockfile')
    return None


def get_lcu_credentials(path):
    path_to_lockfile = path #'D:\Riot\Riot Games\League of Legends/lockfile'#find_lockfile_path()

    if not path_to_lockfile:
        path_to_lockfile = 'lockfile'

    with open(path_to_lockfile, 'r') as file:
        data = file.readline().split(':')
        _, _, port, password, _ = data

    return port, password

def create_lobby():
    endpoint = "/lol-lobby/v2/lobby"
    data = {
        "customGameLobby": {
            "configuration": {
                "gameMode": "CLASSIC",
                "gameMutator": "",
                "gameServerRegion": "",
                "mapId": 11,
                "mutators": {"id": 1},
                "spectatorPolicy": "AllAllowed",
                "teamSize": 5
            },
            "lobbyName": "My Custom Lobby",
            "lobbyPassword": ""
        },
        "isCustom": True
    }

    response = requests.post(f"{LCU_URL}{endpoint}", json=data, headers=HEADERS, auth=AUTH, verify=False)
    return response


def test():
    response = requests.get("https://fix-botbychopa.herokuapp.com/api/greet", verify=False)
    return response


def test2():
    response = requests.get("https://fix-botbychopa.herokuapp.com/api/game_list", verify=False)
    return response


def invite_to_lobby(summoner_name):
    data = [{"toSummonerId": summoner_name}]
    invite_url = LCU_URL + "/lol-lobby/v2/lobby/invitations"
    response = requests.post(invite_url, json=data, headers=HEADERS, verify=False, auth=AUTH)
    return response


def fetch_game_data(game_id):
    endpoint = f"/lol-match-history/v1/games/{game_id}"
    response = requests.get(f"{LCU_URL}{endpoint}", headers=HEADERS, auth=AUTH, verify=False)
    return response


def fetch_game_flow_phase():
    endpoint = f"/lol-gameflow/v1/gameflow-phase"
    response = requests.get(f"{LCU_URL}{endpoint}", headers=HEADERS, auth=AUTH, verify=False)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return None

    return response.json()

def fetch_current_game_id():
    endpoint = "/lol-gameflow/v1/session"
    response = requests.get(f"{LCU_URL}{endpoint}", headers=HEADERS, auth=AUTH, verify=False)

    if response.status_code != 200:
        print(f"Error fetching current game ID: {response.status_code}")
        return None

    data = response.json()
    game_id = data["gameData"].get("gameId", None)
    return game_id

def send_data_to_server(sorted_data, server_url):
    json_data = json.dumps(sorted_data)
    response = requests.post(server_url, data=json_data, headers={'Content-Type': 'application/json'}, verify=False)
    return response


