import time
from threading import Lock

import demjson
from flask import request, Flask
from flask_migrate import Migrate
from flask_socketio import emit, SocketIO
import os
# from dust.app import socketio


# 新加入的内容-开始
from sqlalchemy import func
from sqlalchemy.orm import session

from dust.core import db, current_user
from dust.models.user_planet import MsgList, User, Team

thread = None
thread_lock = Lock()
conns = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
db.init_app(app)
config = os.environ.get('DUST_CONFIG', 'dust.config.DevConfig')
app.config.from_object(config)
Migrate(app, db)



def background_thread(message):
#     """Example of how to send server generated events to clients."""
#     while True:
#         socketio.sleep(5) # 每五秒发送一次
        socketio.emit('get_msg',message, namespace='/websocket/user_refresh')


# 新加入的内容-开始
@socketio.on('connect', namespace='/websocket/user_refresh')
def connect():
    """ 服务端自动发送通信请求 """
    print('=='*10,'已连接')


@socketio.on('connect_event', namespace='/websocket/user_refresh')
def connect_event(message):
    """ 服务端接受客户端发送的通信请求 """
    sid = request.sid
    user_id = message['user_id']
    if user_id == None:
        print('没有登陆！！！')
        return
    conns[user_id] = sid
    msl = db.session.query(MsgList).filter(MsgList.to_id == user_id).order_by(MsgList.created_at.desc())
    members = [dict(demjson.decode(m.msg)) for m in msl]


    # msl1 = db.session.query(MsgList).filter( MsgList.to_id == user_id, MsgList.istalk ==None ).order_by(MsgList.created_at.desc())
    # members1 = [dict(demjson.decode(m.msg)) for m in msl1]
    # members = members + members1
    # msl2 = db.session.query(MsgList).filter(MsgList.from_id == user_id , MsgList.istalk==1).order_by(MsgList.created_at.desc())
    # members2 = [dict(msg=demjson.decode(m.msg),tid=m.id) for m in msl2]
    # print(members2)
    # result = {}
    # result['msl'] = members
    # result['msl2'] = members2

    socketio.emit('init_msg', data=members, room=sid, namespace='/websocket/user_refresh')
    print('**'*10,conns)


@socketio.on('send_message', namespace='/websocket/user_refresh')
def send_message(message):

    print('send_message',message)
    user_id = message['from_id']
    if user_id == None:
        return
    user = User.query.get(user_id)
    isgroup = message['isgroup']

    # {url: 'images/8.png', name: '5', id: 5, txt: `I’m`, time: '2016/06/16', readstate: 0, isgroup: 0, apply: 0},
    message['avatar'] = user.avatar
    # message['avatar'] = user.avatar
    message['name'] = user.hacker_name
    message['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    message['apply'] = 0
    message['id'] = user_id
    if isgroup == 1:
        print('&&'*10,'群组消息')
        us = User.query.filter_by(cteam_id =user.cteam_id)
        message['name'] = "TeamName"
        message['id'] = 'group_' + str(user.cteam_id)
        message['from_id'] = 'group_' + str(user.cteam_id)
        for u in us:
            if u.id == user_id:
                continue
            if u.id in conns.keys():
                sid = conns[u.id]
                socketio.emit('get_msg', data=message, room=sid, namespace='/websocket/user_refresh')

    else:

        conns[user_id] = request.sid
        to_id = message['to_id']
        if to_id in conns.keys():
            to_sid = conns[to_id]
            socketio.emit('get_msg', data=message, room=to_sid, namespace='/websocket/user_refresh')
            print('======='*10)
        print('**id**'*10,message)


    # msgLIst = MsgList()
    # msgLIst.from_id=message['from_id']
    # msgLIst.to_id=message['to_id']
    # msgLIst.msg = demjson.encode(message)
    # print(demjson.encode(message))
    # db.session.add(msgLIst)
    # db.session.commit()


@socketio.on('talk_sync', namespace='/websocket/user_refresh')
def send_message(message):

    msgLIst = MsgList()
    msgLIst.from_id = message['userid']
    msgLIst.msg = demjson.encode(message['result'])
    msgLIst.istalk = 1
    # MsgList.query.get(uid)
    db.session.add(msgLIst)
    db.session.commit()


@socketio.on('add_group', namespace='/websocket/user_refresh')
def send_message(message):
    print(message)
    from_id = message['from_id']
    to_id = message['to_id']
    us = User.query.get(to_id)
    u = dict(avatar=us.avatar, name=us.hacker_name, intro=us.slogan, uid=us.id,cteam_id=us.cteam_id)

    # {url: 'images/6.png', name: '4', id: 4, txt: `I’m glad to join your team  `, time: '2016/06/16', readstate: 0, isgroup: 0, apply: 1}
    result = {}
    result['avatar'] = u['avatar']
    result['name'] = u['name']
    result['id'] = from_id
    result['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    result['readstate'] = 0
    result['isgroup'] = 0
    result['apply'] = 1
    result['isinvitation'] = message['isinvitation']

    if message['isinvitation'] ==1:
        result['txt'] = '邀请您加入:  ' + message['msg']
    else:
        result['txt'] = '我想加入团队:  ' + message['msg']

    result1 = {}
    result1['avatar'] = us.avatar
    result1['name'] = us.hacker_name
    result1['id'] = to_id
    result1['msg'] = '请耐心等待确认！'
    result1['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    result1['from_id'] = to_id
    result1['to_id'] = from_id
    result1['isgroup'] = 0

    if from_id in conns.keys() and to_id in conns.keys():
        from_sid = conns[from_id]
        to_sid = conns[to_id]
        socketio.emit('get_join', data=result, room=to_sid, namespace='/websocket/user_refresh')
        socketio.emit('get_msg', data=result1, room=from_sid, namespace='/websocket/user_refresh')


    print(message,result)
    #保存确认
    msgLIst = MsgList()

    msgLIst.from_id = from_id
    msgLIst.to_id = to_id
    msgLIst.msg = demjson.encode(result)



    #保存返回说明
    msgLIst1 = MsgList()
    msgLIst1.from_id = to_id
    msgLIst1.to_id = from_id
    msgLIst1.msg = demjson.encode(result1)


    db.session.add(msgLIst)
    db.session.add(msgLIst1)
    db.session.commit()


@socketio.on('add_group_judge', namespace='/websocket/user_refresh')
def send_message(message):
    print(message)

    from_id = message['from_id']
    to_id = message['to_id']
    to_sid = conns[to_id]
    from_sid = conns[from_id]

    fus = User.query.get(from_id)

    # 返回确认信息
    result = {}
    result['avatar'] = fus.avatar
    result['name'] = fus.hacker_name
    result['msg'] = '加入成功！！'
    result['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    result['isgroup'] = 0

    if message['isNO'] ==1:
        result['from_id'] = to_id
        result['id'] = to_id
        result['msg'] = '已拒绝'
        result['to_id'] = from_id
        socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')

        result['from_id'] = from_id
        result['id'] = from_id
        result['to_id'] = to_id
        socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
        return

    isinvitation = message['isinvitation']
    if isinvitation == 1:

        # 现在是否以加入团队
        if fus.cteam_id != 0:

            result['from_id'] = to_id
            result['id'] = to_id
            result['msg'] = '已有团队，不能添加'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')

            result['from_id'] = from_id
            result['id'] = from_id
            result['to_id'] = to_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return

        # 接受邀请后是否队伍数量已满
        us = User.query.get(to_id)
        fus_t = User.query.filter_by(cteam_id=us.cteam_id)
        fus_count = fus_t.with_entities(func.count(User.id)).scalar()
        # 邀请方团队是否超过最大数量
        if fus_count > 6:

            result['from_id'] = to_id
            result['id'] = to_id
            result['msg'] = '团队达到最大数量'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')

            result['from_id'] = from_id
            result['id'] = from_id
            result['to_id'] = to_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return

        fus.cteam_id = us.cteam_id
        t = Team.query.get(us.cteam_id)
        t.users.append(fus)
        db.session.commit()

        # 返回群的信息
        # result_group = {}
        # result_group['avatar'] = fus.avatar
        # result_group['name'] = 'TeamName'
        # result_group['id'] = 'group_'+str(us.cteam_id)
        # result_group['msg'] = 'Join the success'
        # result_group['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
        # result_group['from_id'] = 'group_'+str(us.cteam_id)
        # result_group['to_id'] = to_id
        # result_group['isgroup'] = 1

        # {avatar: 'images/7.png', msg: 'What if we make a power machine to getc' man: 'self', read: 0, from_id: '5', to_id: 6, isgroup: 0}
        # {avatar: 'images/6.png', msg: `What if we make a power machine to get
        # the arc.deepened?`, man: 'other', read: 1, from_id: '5', to_id: 7, isgroup: 0}

        # socketio.emit('get_msg', data=result_group, room=to_sid, namespace='/websocket/user_refresh')
        # socketio.emit('get_msg', data=result_group, room=from_sid, namespace='/websocket/user_refresh')



    else:
        # 邀请方是否加入或创建了团队
        if (fus.cteam_id == 0):
            result['from_id'] = to_id
            result['id'] = to_id
            result['msg'] = '无团队！！'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')

            result['from_id'] = from_id
            result['id'] = from_id
            result['to_id'] = to_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return

        # 接受邀请后是否队伍数量已满
        fus_t = User.query.filter_by(cteam_id=fus.cteam_id)
        fus_count = fus_t.with_entities(func.count(User.id)).scalar()
        # 邀请方团队是否超过最大数量
        if fus_count > 6:

            result['from_id'] = to_id
            result['id'] = to_id
            result['msg'] = '团队达到最大数量'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')

            result['from_id'] = from_id
            result['id'] = from_id
            result['to_id'] = to_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return

        us = User.query.get(to_id)
        # 被邀请是否有团队
        if us.cteam_id != 0:
            result['from_id'] = to_id
            result['id'] = to_id
            result['msg'] = '已有团队！！'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')

            result['from_id'] = from_id
            result['id'] = from_id
            result['to_id'] = to_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return

        us.cteam_id = fus.cteam_id
        t = Team.query.get(fus.cteam_id)
        t.users.append(us)
        db.session.commit()

        # 返回群的信息
        # result_group = {}
        # result_group['avatar'] = fus.avatar
        # result_group['name'] = 'TeamName'
        # result_group['id'] = 'group_'+str(us.cteam_id)
        # result_group['msg'] = 'Join the success'
        # result_group['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
        # result_group['from_id'] = 'group_'+str(us.cteam_id)
        # result_group['to_id'] = to_id
        # result_group['isgroup'] = 1

        # {avatar: 'images/7.png', msg: 'What if we make a power machine to getc' man: 'self', read: 0, from_id: '5', to_id: 6, isgroup: 0}
        # {avatar: 'images/6.png', msg: `What if we make a power machine to get
        # the arc.deepened?`, man: 'other', read: 1, from_id: '5', to_id: 7, isgroup: 0}

    result['from_id'] = to_id
    result['id'] = to_id
    result['to_id'] = from_id
    socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')

    result['from_id'] = from_id
    result['id'] = from_id
    result['to_id'] = to_id
    socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')


@socketio.on('exit_group', namespace='/websocket/user_refresh')
def exit_group(message):
    print(message)
    from_id = message['from_id']
    user = User.query.get(from_id)
    us = User.query.filter_by(cteam_id =user.cteam_id)

    result = {}
    result['avatar'] = user.avatar
    result['name'] = user.hacker_name
    result['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    result['isgroup'] = 0

    if user.cteam_id != 0:

        if user.is_admin ==0:
            user.cteam_id=0
        else:
            for u in us:
                u.cteam_id=0

        db.session.commit()
        for u in us:
            if u.id == from_id:
                continue

            if u.id in conns.keys():
                sid = conns[u.id]

                result['from_id'] = from_id
                result['id'] = from_id
                result['to_id'] = u.id
                result['msg'] = '退出组队！！'
                socketio.emit('get_msg', data=result, room=sid, namespace='/websocket/user_refresh')

    else:

        result['from_id'] = from_id
        result['id'] = from_id
        result['to_id'] = from_id
        result['msg'] = '没有队伍！！！无法退出！'
        sid = conns[from_id]
        socketio.emit('get_msg', data=result, room=sid, namespace='/websocket/user_refresh')


if __name__ == '__main__':
    socketio.run(app,port=5200, debug=True,host='0.0.0.0')