from .db_func import make_reservation_db
from .db_func import reservation
from .db_func import search_reservation
from .db_func import cancel_reservation
from .db_func import my_reservation
from . import library_crawl

import urllib.request
from bs4 import BeautifulSoup
import json
import os
import sqlite3
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def keyboard(request):

    print(request.body)
    menus = ['예약현황', '예약하기', '예약취소']

    return JsonResponse({
        'type': "buttons",
        "buttons": menus,
    })

@csrf_exempt
def message(request):
    menus = ['예약하기', '예약취소', '나의 예약현황', '도서관']
    study_room_menu = ['1번실', '2번실', '3번실', '4번실', '5번실', '6번실']

    req = (request.body).decode('utf-8')
    received_json = json.loads(req)

    content_name = received_json['content']
    user_name = received_json['user_key']

    now_date = datetime.datetime.now()
    now_date = now_date.strftime("%H%M")
    ## 183700 > 164700 + 30000
    # 18시37분00초

    if not os.path.exists("./DB"):
        make_reservation_db()  # 생성하게끔
        # DB폴더없으면

    if content_name == '나의 예약현황':
        reservation_MyStatus = my_reservation({"student": user_name})
        # 리턴형식 : [방번호, 사용할 시간, 예약당시 시간, 패스워드]
        text = "사용자의 예약현황\n"
        for cell in reservation_MyStatus:
            if len(cell[1]) == 3:
                time = "{}시 {}분".format(cell[1][:1], cell[1][1:])
            else:
                time = "{}시 {}분".format(cell[1][:2], cell[1][2:])

            text += "{} - {}\n비밀번호 : {}\n".format(cell[0], time, cell[3])

        return JsonResponse({
            "message": {
                "text": text
            },
            "keyboard": {
                "type": "buttons",
                "buttons": menus
            }
        })

    elif content_name == '예약하기':
        # '예약하기' => '번실' => '번실 - '
        me = ['1번실', '2번실', '3번실', '4번실', '5번실']
        return JsonResponse({
            "message": {
                "text": "스터디룸을 선택해주세요"
            },
            "keyboard": {
                "type": "buttons",
                "buttons": me
            }
        })

    elif '번실 - ' in content_name and len(content_name) < 20:
        time_sen = str(content_name[6:])

        time_sen = time_sen.replace('시', '').replace('분','').replace(' ','')
        reserve_data = {
            "NO": content_name[:1],
            "reservation_time": now_date,
            "student": user_name,
            "start_time": time_sen,
        }

        result = reservation(reserve_data)
        # 정상 0, 비정상종료는 1, 예약한 곳이 있으면 5 리턴

        if result["code"] == 0:
            return JsonResponse({
                "message": {
                    "text": "{} 예약되었습니다\n비밀번호 : {}"
                        .format(content_name, result["password"])
                },
                "keyboard": {
                    "type": "buttons",
                    "buttons": menus
                }
            })
        elif result["code"] == 1:
            return JsonResponse({
                "message": {
                    "text": "예약중 오류가 발생했습니다\n개발자에게 말씀해주세요"
                },
                "keyboard": {
                    "type": "buttons",
                    "buttons": menus
                }
            })
        elif result["code"] == 5:
            return JsonResponse({
                "message": {
                    "text": "이미 3시간을 모두 소진하였습니다\n취소후 다시 예약해주세요"
                },
                "keyboard": {
                    "type": "buttons",
                    "buttons": menus
                }
            })
        elif result["code"] == 7:
            return JsonResponse({
                "message": {
                    "text": "이미 지난 시간입니다."
                },
                "keyboard": {
                    "type": "buttons",
                    "buttons": menus
                }
            })

    elif '번실' in content_name and len(content_name) < 20:
        available_list = search_reservation()
        room_no = content_name[:1]
        can_select = []
        print(available_list)
        time = datetime.datetime.now().strftime("%H%M")
        for can_time in available_list['ROOM' + room_no]:
            if int(can_time) < int(time):
                continue
                #시간지나면 예약화면 안뜨게
            print(can_time)
            if len(can_time) == 1:
                can_time = "{}시 {}분".format(can_time[0:1], "00")
            elif len(can_time) == 3:
                can_time = "{}시 {}분".format(can_time[0:1], can_time[1:])
            elif len(can_time) == 4:
                can_time = "{}시 {}분".format(can_time[0:2], can_time[2:])

            # can_select는 가능한 호실들 response하기위한 목록
            # can_time은 available_list 해당호실의 예약가능한 시간들
            can_select.append("{} - {}".format(content_name, can_time))
                # '2번실 - 9시 30분'
                # 분류는 '번실 - ' 로 하면된다.
        #print(can_select)
        #print('\n\n')
        print(can_select)

        mes_text = "예약 화면"

        if can_select == []:
            mes_text = "빈 방이 없습니다"
            can_select = ['예약하기', '예약취소', '나의 예약현황']

        return JsonResponse({
            "message": {
                "text": mes_text
            },
            "keyboard": {
                "type": "buttons",
                "buttons": can_select
            }
        })

    elif '예' == content_name:
        res = cancel_reservation({"student": user_name})
        return JsonResponse({
            "message": {
                "text": "{}".format(res)
            },
            "keyboard": {
                "type": "buttons",
                "buttons": menus
            }
        })

    elif '아니오' == content_name:
        return JsonResponse({
            "message": {
                "text": "예약취소를 하지않습니다\n메인으로 이동합니다"
            },
            "keyboard": {
                "type": "buttons",
                "buttons": menus
            }
        })

    elif content_name == '예약취소':
        return JsonResponse({
            "message": {
                "text": "예약취소하시겠습니까?"
            },
            "keyboard": {
                "type": "buttons",
                "buttons": ['예', '아니오']
            }
        })

    elif content_name == '도서관':
        try:
            req = urllib.request.urlopen('http://203.232.237.8/domian5/2/domian5.asp')
        except:
            pass

        soup = BeautifulSoup(req, 'lxml', from_encoding="utf-8")

        my_titles = soup.select(
            'tr'
        )
        data = []
        for title in my_titles:
            data.append(title.text)

        # data[3]은 3층 1열람실 내용
        # [3~7]까지의 (6)

        if content_name == "도서관":
            lib_data =  {'3-1': data[3].split()[6], '3-2': data[4].split()[6], '4-3A': data[5].split()[6],
                    '4-3B': data[6].split()[6]}
        else:
            # #print(data[name+2].split())
            lib_data  = {'%': data[name + 2].split()[6], '이용자': data[name + 2].split()[4],
                    '남은 좌석': data[name + 2].split()[5]}

        if lib_data == 555:
            return JsonResponse({
                'message': {
                    'text': "도서관 좌석을 불러 올 수 없습니다.\n다시 이용해주세요",
                },
                'keyboard': {
                    'type': 'buttons',
                    'buttons': button_info
                }
            })

        buttons = ['3층 1열람실: ' + str(lib_data['3-1']) + '%',
                   '3층 2열람실: ' + str(lib_data['3-2']) + '%',
                   '4층 3열람실A: ' + str(lib_data['4-3A']) + '%',
                   '4층 3열람실B: ' + str(lib_data['4-3B']) + '%'
                   ]

        return JsonResponse({
            'message': {
                'text': '열람실을 선택하세요'
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': buttons
            }
        })


    elif '열람실' in content_name:

        if '3층 1열람실: ' in content_name:

            name = "3층 1열람실 현황: "
            lib_num = 1
            room_no = 8

        elif '3층 2열람실: ' in content_name:

            name = "3층 2열람실 현황: "
            lib_num = 2
            room_no = 9

        elif '4층 3열람실A: ' in content_name:

            name = "4층 3열람실A 현황: "
            lib_num = 3
            room_no = 10

        elif '4층 3열람실B: ' in content_name:

            name = "4층 3열람실B 현황: "
            lib_num = 4
            room_no = 11

        lib_data = library_crawl.glo_library(lib_num)

        return JsonResponse({
            'message': {
                'text': name + str(lib_data['%']) + '%' + '\n이용자 수: ' + str(lib_data['이용자']) +
                        '명\n남은 좌석 수: ' + str(lib_data['남은 좌석']),
                'message_button': {
                       'label': '좌석보기',
                       'url': 'http://203.232.237.8/domian5/roomview5.asp?room_no=' + str(room_no)
                }
            },
            'keyboard': {
                'type': 'buttons',
                'buttons': menus
            }
           })

    else:
        return JsonResponse({
            "message": {
                "text": "오류입니다."
            },
            "keyboard": {
                "type": "buttons",
                "buttons": menus
            }
        })

