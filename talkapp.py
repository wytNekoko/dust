import time
from threading import Lock

from flask import request, Flask
from flask_migrate import Migrate
from flask_socketio import emit, SocketIO
import os
# from dust.app import socketio


# 新加入的内容-开始
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
    conns[user_id] = sid
    print('**'*10,message)


@socketio.on('send_message', namespace='/websocket/user_refresh')
def send_message(message):
    """ 服务端接受客户端发送的通信请求 """
    # message['user_id']
    # socketio.emit('user_response', {'data': users_to_json}, namespace='/websocket/user_refresh')
    # with thread_lock:
    #     if thread != None:
    #         socketio.start_background_task(target=background_thread,args=(message,))

    print(message)
    user_id =  message['from_id']
    if user_id == None:
        return
    isgroup = message['isgroup']
    if isgroup == 1:
        print('&&'*10,'群组消息')
        user = User.query.get(user_id)
        us = User.query.filter_by(cteam_id =user.cteam_id)
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
    result['txt'] = '`I’m glad to join your team  `'
    result['time'] = time.strftime("%Y/%m/%d %H", time.localtime())
    result['readstate'] = 0
    result['isgroup'] = 0
    result['apply'] = 1
    to_sid = conns[to_id]
    socketio.emit('get_join', data=result, room=to_sid, namespace='/websocket/user_refresh')
    print(message,result)



@socketio.on('add_group_judge', namespace='/websocket/user_refresh')
def send_message(message):
    print(message)
    isinvitation = message['isinvitation']
    if isinvitation == 0:
        from_id = message['from_id']
        to_id = message['to_id']
        fus = User.query.get(from_id)
        us = User.query.get(to_id)
        us.cteam_id = fus.cteam_id
        db.session.commit()



if __name__ == '__main__':
    socketio.run(app,port=5200, debug=True,host='0.0.0.0')