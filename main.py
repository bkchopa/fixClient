import tkinter as tk
from tkinter import ttk
import lcu
import api
import time
import threading

import requests
print(requests.certs.where())

import ssl
print(ssl.OPENSSL_VERSION)

def get_sorted_data(data):
    positions_order = ["TOP", "JUG", "MID", "ADC", "SUP", "UNKNOWN"]

    winning_team = [player for player in data if player['win'] == 'Win']
    losing_team = [player for player in data if player['win'] != 'Win']

    sorted_winning_team = sorted(winning_team, key=lambda x: positions_order.index(x['position']))
    sorted_losing_team = sorted(losing_team, key=lambda x: positions_order.index(x['position']))

    sorted_data = sorted_winning_team + sorted_losing_team
    return sorted_data

def determine_position(lane, role):
    if lane == "TOP":
        return "TOP"
    elif lane == "JUNGLE" or (lane == "NONE" and role == "NONE"):
        return "JUG"
    elif lane == "MIDDLE":
        return "MID"
    elif lane == "BOTTOM" and role == "CARRY":
        return "ADC"
    elif lane == "BOTTOM" and role == "SUPPORT":
        return "SUP"
    else:
        return "UNKNOWN"

class App:
    def __init__(self, root):
        # ... [기존 init 함수 내용 생략]

        self.LAST_PHASE = None
        self.current_game_id = None  # 현재 게임의 ID를 저장하는 변수

        self.monitor_thread = threading.Thread(target=self.monitor_game_flow_phase, daemon=True)

        self.left_frame = ttk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, padx=20, pady=20)

        self.right_frame = ttk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

        self.create_button = ttk.Button(self.left_frame, text="방 생성 및 초대", command=self.create_lobby)
        self.create_button.pack(pady=20)

        self.test_button = ttk.Button(self.left_frame, text="테스트", command=self.run_test)
        self.test_button.pack(pady=20)

        self.test_button2 = ttk.Button(self.left_frame, text="테스트2", command=self.run_test)
        self.test_button2.pack(pady=20)

        self.label = ttk.Label(self.right_frame, text="소환사 닉네임:")
        self.label.pack(pady=10)

        self.entry = ttk.Entry(self.right_frame, width=20)
        self.entry.pack(pady=10)

        self.invite_button = ttk.Button(self.right_frame, text="초대", command=self.invite)
        self.invite_button.pack(pady=10)

        # 게임 ID 입력 및 정보 가져오기 위한 UI 요소
        self.game_id_label = ttk.Label(self.right_frame, text="게임 ID:")
        self.game_id_label.pack(pady=10)

        self.game_id_entry = ttk.Entry(self.right_frame, width=20)
        self.game_id_entry.pack(pady=10)

        self.fetch_game_data_button = ttk.Button(self.right_frame, text="게임 정보 가져오기", command=self.fetch_game_data)
        self.fetch_game_data_button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=20)

        self.master = root
        self.master.title("LCU Path Input")

        self.root = root
        self.root.title("LCU Path Input")

        self.label = tk.Label(root, text="Enter the path to the League of Legends folder:")
        self.label.pack(pady=20)

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=20)

        self.submit_button = tk.Button(root, text="Submit", command=self.set_path)
        self.submit_button.pack(pady=20)

    def create_lobby(self):
        # Use the API function to create lobby
        response = lcu.create_lobby()
        if response.status_code == 200:
            self.result_label.config(text="Lobby created successfully!")
        else:
            self.result_label.config(text=f"Error creating lobby: {response.text}")

    def invite(self):
        summoner_name = self.entry.get()
        response = lcu.invite_to_lobby(summoner_name)
        if response.status_code == 204:
            self.result_label.config(text=f"Invited {summoner_name} to the lobby!")
        else:
            self.result_label.config(text=f"Error inviting: {response.text}")

    def run_test(self):
        response = lcu.test()
        if response.status_code == 200:
            self.result_label.config(text="Connected successfully!")
        else:
            self.result_label.config(text=f"Connection error: {response.text}")

    def fetch_game_data(self):
        game_id = self.game_id_entry.get()
        response = lcu.fetch_game_data(game_id)
        if response.status_code == 200:
            match_data = response.json()

            participants_data = match_data['participants']
            participant_identities = match_data['participantIdentities']

            # 결과 데이터를 생성합니다.
            result_data = []
            for participant, identity in zip(participants_data, participant_identities):
                player_data = {}
                player_data['nickname'] = identity['player']['summonerName']
                player_data['champion'] = str(participant['championId'])
                player_data['win'] = 'Win' if participant['stats']['win'] else 'Lose'
                player_data['position'] = determine_position(participant['timeline']['lane'],
                                                             participant['timeline']['role'])
                player_data['kills'] = participant['stats'].get('kills', 0)
                player_data['deaths'] = participant['stats'].get('deaths', 0)
                player_data['assists'] = participant['stats'].get('assists', 0)

                result_data.append(player_data)

            # 데이터를 정렬하고 출력합니다.
            sorted_data = get_sorted_data(result_data)

            payload = {
                "game_data": sorted_data,
                "game_id": game_id
            }
            print(payload)
            api.send_json_to_server("api/game_result", payload)

        else:
            print(f"Error {response.status_code}: {response.text}")

    def fetch_and_process_game_data(self, game_id):
        response = lcu.fetch_game_data(game_id)
        if response.status_code == 200:
            match_data = response.json()

            participants_data = match_data['participants']
            participant_identities = match_data['participantIdentities']

            # 결과 데이터를 생성합니다.
            result_data = []
            for participant, identity in zip(participants_data, participant_identities):
                player_data = {}
                player_data['nickname'] = identity['player']['summonerName']
                player_data['champion'] = str(participant['championId'])
                player_data['win'] = 'Win' if participant['stats']['win'] else 'Lose'
                player_data['position'] = determine_position(participant['timeline']['lane'],
                                                             participant['timeline']['role'])
                player_data['kills'] = participant['stats'].get('kills', 0)
                player_data['deaths'] = participant['stats'].get('deaths', 0)
                player_data['assists'] = participant['stats'].get('assists', 0)

                result_data.append(player_data)

            # 데이터를 정렬하고 출력합니다.
            sorted_data = get_sorted_data(result_data)

            payload = {
                "game_data": sorted_data,
                "game_id": game_id
            }
            print(payload)
            api.send_json_to_server("api/game_result", payload)

        else:
            print(f"Error {response.status_code}: {response.text}")

    def onGameFlowPhaseChanged(self, new_phase):
        # 여기에 게임 플로우 상태가 변경되었을 때의 처리 로직을 추가하십시오.
        if new_phase != "InProgress" and self.current_game_id:
            self.fetch_and_process_game_data(self.current_game_id)
            self.current_game_id = None
        if new_phase == "InProgress":
            self.current_game_id = lcu.fetch_current_game_id()
            if self.current_game_id:
                print(f"Game is in progress. Current game ID: {self.current_game_id}")

    def set_path(self):
        path_to_lol = self.entry.get()
        path_to_lockfile = path_to_lol + '/lockfile'

        port, password = lcu.get_lcu_credentials(path_to_lockfile)
        LCU_URL = f"https://127.0.0.1:{port}"
        HEADERS = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        AUTH = ('riot', password)

        # 전역 변수 설정
        lcu.set_lcu_globals(LCU_URL, HEADERS, AUTH)


        self.monitor_thread.start()


    def monitor_game_flow_phase(self):
        while True:
            # 1분 대기
            api.test_greet()
            time.sleep(60)
            current_phase = lcu.fetch_game_flow_phase()
            print(current_phase)
            if current_phase is None:
                continue
            elif current_phase != self.LAST_PHASE:
                self.onGameFlowPhaseChanged(current_phase)
                self.LAST_PHASE = current_phase







if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
