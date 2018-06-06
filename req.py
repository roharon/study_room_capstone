import requests
import json
import datetime

"""
requests이용한 사용자요청마다 비번받을 경우의 스크립트

"""

def password():
    now_time = datetime.datetime.now()

    str_time = now_time.strftime('%H') + "00"
    # str_time은 현시간대의 비밀번호 알아내기 위해서
    # 특정시간대로 하려면 임의로 data에서 1300 이렇게 설정하면됩니다.

    data = {'room': str(2),
            'start_time': str(int((str_time)))}

    data_json = json.dumps(data)
    #print(payload)
    r = requests.get('http://35.189.136.35:8005/password', data=data_json)
    #r = requests.get('http://127.0.0.1:8000/password', data=payload)
    print(r.json())

def all_password():
    data = {'room': '2',
            }
    data_json = json.dumps(data)

    r = requests.get('http://35.189.136.35:8005/all_pw', data=data_json)
    #r = requests.get('http://127.0.0.1:8000/all_password', data=payload)
    print(r.json())

if __name__ == "__main__":
    all_password()