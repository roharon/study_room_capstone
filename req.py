import requests
import json

data = {'room': 2,
        'start_time': 1300, }

data_json = json.dumps(data)
payload = {'json_payload': data_json}

r = requests.get('http://35.189.136.35:8005/password', data=payload)
print(r.json())