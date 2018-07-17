from threading import Lock

from flask import request, Flask
from flask_migrate import Migrate
from flask_socketio import emit, SocketIO
import os
# from dust.app import socketio


# 新加入的内容-开始
from dust.core import db
from dust.models.user_planet import MsgList

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


if __name__ == '__main__':
    socketio.run(app,port=5200, debug=True,host='0.0.0.0')