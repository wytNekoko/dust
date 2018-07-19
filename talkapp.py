import time
from threading import Lock

from flask import request, Flask
from flask_migrate import Migrate
from flask_socketio import emit, SocketIO
import os
# from dust.app import socketio


# 新加入的内容-开始
from sqlalchemy import func

from dust.core import db, current_user
from dust.models.user_planet import MsgList, User

thread = None
thread_lock = Lock()
conns = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
async_mode = 'eventlet'
socketio = SocketIO(app, async_mode=async_mode)
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
        return
    conns[user_id] = sid
    print('**'*10,conns)


@socketio.on('send_message', namespace='/websocket/user_refresh')
def send_message(message):
    """ 服务端接受客户端发送的通信请求 """

    print('send_message',message)
    user_id =  message['from_id']
    if user_id == None:
        return
    user = User.query.get(user_id)
    isgroup = message['isgroup']
    # // obj['avatar']
    # // result['name'] = obj['name']
    # {url: 'images/8.png', name: '5', id: 5, txt: `I’m`, time: '2016/06/16', readstate: 0, isgroup: 0, apply: 0},
    message['avatar'] = user.avatar
    message['avatar'] = user.avatar
    message['name'] = user.hacker_name
    message['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    message['apply'] = 0
    if isgroup == 1:
        print('&&'*10,'群组消息')
        us = User.query.filter_by(cteam_id =user.cteam_id)
        message['name'] = "TeamName"
        message['id'] = 'group_' + str(user_id)
        message['id'] = user_id
        for u in us:
            if u.id == user_id:
                continue
            sid = conns[u.id]
            socketio.emit('get_msg', data=message, room=sid, namespace='/websocket/user_refresh')
    else:
        msgLIst = MsgList()
        msgLIst.msg = message['msg']
        # MsgList.query.get(uid)
        db.session.add(msgLIst)
        db.session.commit()
        conns[user_id] = request.sid
        to_id = message['to_id']
        print(conns)
        if to_id in conns.keys():
            to_sid = conns[to_id]
            print(conns[to_id])
            socketio.emit('get_msg', data=message, room=to_sid, namespace='/websocket/user_refresh')
            print('======='*10)
        print('**id**'*10,message)


@socketio.on('add_group', namespace='/websocket/user_refresh')
def send_message(message):
    """ 服务端接受客户端发送的通信请求 """
    print(message)
    from_id = message['from_id']
    to_id = message['to_id']
    fus = User.query.get(from_id)
    us = User.query.get(to_id)
    # fu = dict(url=fus.avatar, name=fus.hacker_name, intro=fus.slogan, uid=fus.id, cteam_id=fus.cteam_id)
    u = dict(url=us.avatar, name=us.hacker_name, intro=us.slogan, uid=us.id,cteam_id=us.cteam_id)
    # {url: 'images/6.png', name: '4', id: 4, txt: `I’m glad to join your team  `, time: '2016/06/16', readstate: 0, isgroup: 0, apply: 1}
    result = {}
    result['url'] = u['url']
    result['name'] = u['name']
    result['id'] = from_id
    result['txt'] = 'Add group invited:'+message['msg']
    result['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    result['readstate'] = 0
    result['isgroup'] = 0
    result['apply'] = 1
    result['isinvitation'] = message['isinvitation']
    to_sid = conns[to_id]
    socketio.emit('get_join', data=result, room=to_sid, namespace='/websocket/user_refresh')
    print(message,result)



@socketio.on('add_group_judge', namespace='/websocket/user_refresh')
def send_message(message):
    print(message)

    from_id = message['from_id']
    to_id = message['to_id']
    to_sid = conns[to_id]
    from_sid = conns[from_id]
    isinvitation = message['isinvitation']
    if isinvitation == 1:

        fus = User.query.get(from_id)
        # 返回确认信息
        result = {}
        result['avatar'] = fus.avatar
        result['name'] = fus.hacker_name
        result['id'] = from_id
        result['msg'] = 'Join the success'
        result['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
        result['from_id'] = from_id
        result['to_id'] = to_id
        result['isgroup'] = 0


        #现在是否以加入团队
        if (fus.cteam_id !=0):
            result['avatar'] = fus.avatar
            result['name'] = 'Administrator'
            result['from_id'] = -1
            result['id'] = -1
            result['msg'] = '已加入团队'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=from_sid, namespace='/websocket/user_refresh')
            return

        # 接受邀请后是否队伍数量已满
        us = User.query.get(to_id)
        fus_t = User.query.filter_by(cteam_id=us.cteam_id)
        fus_count = fus_t.with_entities(func.count(User.id)).scalar()
        # 邀请方团队是否超过最大数量
        if (fus_count > 5):
            result['avatar'] = fus.avatar
            result['name'] = 'Administrator'
            result['from_id'] = -1
            result['msg'] = '您团队超过最大数量'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return




        us.cteam_id = fus.cteam_id
        db.session.commit()

        # 返回群的信息
        result_group = {}
        result_group['avatar'] = fus.avatar
        result_group['name'] = 'TeamName'
        result_group['id'] = 'group_'+str(from_id)
        result_group['msg'] = 'Join the success'
        result_group['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
        result_group['from_id'] = 'group_'+str(from_id)
        result_group['to_id'] = to_id
        result_group['isgroup'] = 1

        # {avatar: 'images/7.png', msg: 'What if we make a power machine to getc' man: 'self', read: 0, from_id: '5', to_id: 6, isgroup: 0}
        # {avatar: 'images/6.png', msg: `What if we make a power machine to get
        # the arc.deepened?`, man: 'other', read: 1, from_id: '5', to_id: 7, isgroup: 0}

        socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
        socketio.emit('get_msg', data=result_group, room=to_sid, namespace='/websocket/user_refresh')



    else:

        fus = User.query.get(from_id)
        # 返回确认信息
        result = {}
        result['avatar'] = fus.avatar
        result['name'] = fus.hacker_name
        result['id'] = from_id
        result['msg'] = 'Join the success'
        result['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
        result['from_id'] = from_id
        result['to_id'] = to_id
        result['isgroup'] = 0

        # 邀请方是否加入或创建了团队
        if (fus.cteam_id == 0):
            result['avatar'] = fus.avatar
            result['name'] = 'Administrator'
            result['from_id'] = -1
            result['msg'] = '您没有加入或创建团队'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return


        fus_t = User.query.filter_by(cteam_id =fus.cteam_id)
        # 邀请方团队是否超过最大数量
        if (len(fus_t) > 5):
            result['avatar'] = fus.avatar
            result['name'] = 'Administrator'
            result['from_id'] = -1
            result['msg'] = '您团队超过最大数量'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return

        us = User.query.get(to_id)
        # 被邀请是否有团队
        if (us.cteam_id != 0):
            result['avatar'] = fus.avatar
            result['name'] = 'Administrator'
            result['from_id'] = -1
            result['msg'] = '对方以有团队'
            result['to_id'] = from_id
            socketio.emit('get_msg', data=result, room=to_sid, namespace='/websocket/user_refresh')
            return



if __name__ == '__main__':
    socketio.run(app,port=5200, debug=True,host='0.0.0.0')