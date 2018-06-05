import requests
import json
import datetime

now_time = datetime.datetime.now()

str_time = now_time.strftime('%H') + "00"
#str_time은 현시간대의 비밀번호 알아내기 위해서
#특정시간대로 하려면 임의로 data에서 1300 이렇게 설정하면됩니다.

data = {'room': 2,
        'start_time': int(str_time) }

data_json = json.dumps(data)
payload = {'json_payload': data_json}

r = requests.get('http://35.189.136.35:8005/password', data=payload)
print(r.json())