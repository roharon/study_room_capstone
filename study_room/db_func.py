import sqlite3
import os
import datetime
import random
import requests
import json
from django.http import JsonResponse

"""
#make_reservation_db : DB폴더없을때 생성해줌
#reservation : room DB연결하여 예약생성
#reserve_main : 

"""


def make_reservation_db():
    """
    3시간 간격으로 DB 컬럼 채운다.

    start_time | end_time | student | reservation_time 으로 구성되어있으며

    start_time과 end_time은 개발자가 지정(0930~2130), student는 예약자 이름,
    reservation_text는 사용자 예약당시의 시간이다.

    """
    path = "../DB"
    os.makedirs(path, exist_ok=True)
    os.remove("../DB/room")
    con = sqlite3.connect('../DB/room')

    cur = con.cursor()

    for i in range(1, 6):
        cur.execute("CREATE TABLE ROOM" + str(i) + "(start_time text, end_time text, student text, reservation_time text, password text)")

        time_res = 100
        for j in range(0, 2400, time_res):
            randpassword = random.randrange(1000,10000)
            cur.execute("INSERT INTO ROOM" + str(i) + " Values(:start_time, :end_time, :student, :reservation_time, :password);",
                        {"start_time": j, "end_time": j + time_res, "student": '', "reservation_time": '', "password": str(randpassword)})

    con.commit()
    con.close()


def reservation(request = None):
    # NO reservation_time student start_time
    # 정상이면 0 리턴, 비정상 종료면 1리턴, 기존예약이 있으면 5 리턴
    con = sqlite3.connect('./DB/room')
    cur = con.cursor()
    select = []

    for j in range(1, 6):
        user_select_room = cur.execute("SELECT start_time FROM ROOM{} WHERE student = {!r}"
                                       .format(str(j), request['student']))
        for i in user_select_room.fetchall():
            select.append(i)
    print(select)

    # 안비어으면 예약안되게 한다.
    # 예약한 스터디룸이 3   개를 넘어선다 ==> 예약 더이상 안되게 한다.
    if len(select) > 2:
        print(select)
        con.close()
        return {"code": 5}

    now_room = cur.execute("SELECT reservation_time FROM ROOM{0} WHERE start_time = {1};"
                .format(str(request['NO']), str(request['start_time'])))

    now_room = now_room.fetchall()
    # now_room 이 비어있으면 UPDATE 없으면 그대로 리턴
    if now_room == [('',)]:
        cur.execute("UPDATE ROOM{} SET reservation_time = {}, student = {!r} WHERE start_time = {};"
                    .format(str(request['NO']), str(request['reservation_time']), str(request['student']),
                            str(request['start_time'])))
        # sqlite3 포매팅에 !r을 붙이지않으면 unrecognized token 오류가 난다.
    else:
        print(now_room)
        con.close()
        return {"code": 1}

    room_password = cur.execute("SELECT password FROM ROOM{} WHERE start_time = {};"
                                .format(str(request['NO']), str(request['start_time'])))
    room_password = room_password.fetchall()
    con.commit()
    con.close()
    print(room_password[0][0])
    return {"code":0, "password": room_password[0][0]}
    # code 정상종료 확인코드, password 스터디룸 비밀번호


def search_reservation(request = None):
    con = sqlite3.connect('./DB/room')
    cur = con.cursor()

    #now_time = datetime.datetime.now()
    #now_time = int(now_time.strftime("%H%M%S"))

    available_list = {}

    for i in range(1, 6):
        available_list['ROOM' + str(i)] = []
        # 스터디룸 갯수별로 딕셔너리에 리스트 타입으로 만들고 append
        cur.execute("SELECT start_time FROM ROOM{} WHERE reservation_time = '';"
                    .format(str(i)))
        # reservation_time 이 비어있으며, 해당 시간대가 현재 시간보다 나중일 경우만 선택
        # 시간 나중인것은 후에 구현하기로 함. 2018-06-02 21:31
        for cell in cur.fetchall():
            available_list['ROOM' + str(i)].append(cell[0])
            # {'ROOM1': ['1230', '1530', '1830'], 'ROOM2': ['930', '1230', '1530', '1830'], 'ROOM3': ['1530', '1830'],
            # 'ROOM4': ['930', '1230', '1530', '1830'], 'ROOM5': ['930', '1230', '1530', '1830']}

    con.close()
    # print(available_list)

    return available_list

def my_reservation(request = None):
    # student키
    # 나의 예약현황
    reservation_list = []
    #reservation_list 에 [방번호, 사용할 시간, 예약당시 시간]

    con = sqlite3.connect("./DB/room")
    cur = con.cursor()

    for i in range(1,6):
        cur.execute("SELECT start_time, reservation_time, password FROM ROOM{} WHERE student = {!r};"
                    .format(str(i), request['student']))
        for j in cur.fetchall():
            reservation_list.append(['ROOM{}'.format(i), j[0], j[1], j[2]])
    print(reservation_list)

    return reservation_list
    # [['ROOM1', '930', '110', PASSWORD]]

def cancel_reservation(request = None):
    # 리턴 1은 비정상적 종료,
    # student키
    con = sqlite3.connect("./DB/room")
    cur = con.cursor()

    prev_cancel = my_reservation({"student": request['student']})

    try:
        for i in range(len(prev_cancel)):
            cur.execute("UPDATE ROOM{} SET student = '', reservation_time = '' WHERE start_time = {};"
                    .format(prev_cancel[i][0][4:], prev_cancel[i][1]))

    except Exception as e:
        con.close()
        print(e)
        return "취소할 곳이 없습니다"
    con.commit()
    con.close()

    text = ""
    for i in range(len(prev_cancel)):
        time = prev_cancel[i][1]

        if len(time) == 1:
            time = "{}시 00분".format(time)
        elif len(time) == 3:
            time = "{}시 {}분".format(time[:1], time[1:])
        elif len(time) == 4:
            time = "{}시 {}분".format(time[:2], time[2:])

        text += "{}번실 {} 예약 취소되었습니다\n"\
            .format(prev_cancel[i][0][4:], time)
    return text

def rasp_password(request):
    # {'room': 방번호, 'start_time': 시작시간
    # {'room': 1, 'start_time': 200}
    # 1번실 오전2시

    json_res = {'room': 2, 'start_time': 1300}
    con = sqlite3.connect("./DB/room")
    cur = con.cursor()

    #json_reqeust = (request.body).decode('utf-8')
    #json_res = json.loads(json_reqeust)

    cur.execute("SELECT password FROM ROOM{} WHERE start_time = {}"
                .format(str(json_res['room']), str(json_res['start_time'])))

    password = cur.fetchall()

    return JsonResponse({
        'password': password[0]
    })


if __name__ == "__main__":
    make_reservation_db()
    #search_reservation()

    """
    my_reservation({'student': 'roharon'})
    print("===============")
    reservation({
        'NO': '1',
        'student': 'roharon',
        'reservation_time': '0110',
        'start_time': '930',
    })
    """