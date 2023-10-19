import requests
import urllib3
from urllib3.util.ssl_ import create_urllib3_context

ctx = create_urllib3_context()
ctx.load_default_certs()
ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT

with urllib3.PoolManager(ssl_context=ctx) as http:
    r = http.request("GET", "https://nomads.ncep.noaa.gov/")
    print(r.status)


BASE_URL = "https://fix-botbychopa.herokuapp.com/"

def test_greet():
    """테스트용 함수: 서버에 greetings를 요청합니다."""
    response = requests.get(f"{BASE_URL}api/greet", verify=False)
    return response

def send_json_to_server(endpoint, data):
    """서버로 JSON 데이터를 POST 요청으로 전송하는 함수.

    Args:
        endpoint (str): API 엔드포인트. 예: "api/update_data"
        data (dict): 서버로 전송할 JSON 데이터.

    Returns:
        response (Response): 서버로부터의 응답 객체.
    """
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers, verify=False)
    if response.status_code == 200:
        print("Game data sent successfully!")
    else:
        print(f"Error sending game data: {response.text} , Fail: {endpoint}")

    return response