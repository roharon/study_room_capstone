import requests
import json

room_number = 2
"""
room_number에 호실 기입하세요

스크립트 기능
정해진 시간에
해당 스터디룸 비번 모두 가져오기

분 시 일 월 요일 시행할작업
0 6 * * * /~~~~/auto_rasp.py

가상환경에서 돌릴 경우
분 시 일 월 요일 가상환경Python파일위치 시행할작업
0 6 * * * /가상환경python파일 /~~/auto_rasp.py


password.json 파일을 가져올땐 json 
with open('password.json') as f:
     data = json.load(f)
과 같이 텍스트파일 가져오는 것으로 하시면 됩니다.
data['700']을 하면 오전7시의 비번이 나옵니다.
"""

room_path = "./DB/room"

data = {'room': room_number,
            }
data_json = json.dumps(data)

r = requests.get('http://35.189.136.35:8005/all_pw', data=data_json)
#r = requests.get('http://127.0.0.1:8000/all_password', data=payload)
pw_dict = r.json()

with open('password.json', 'w', encoding="utf-8") as f:
    json.dump(pw_dict, f)
print(r.json())