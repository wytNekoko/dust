from threading import Lock

from flask import request
from flask_socketio import emit

from dust.app import socketio


# 新加入的内容-开始

thread = None
thread_lock = Lock()
conns = {}


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
    socketio.emit('get_msg', data='asdasd', room=sid, namespace='/websocket/user_refresh')



@socketio.on('send_message', namespace='/websocket/user_refresh')
def send_message(message):
    """ 服务端接受客户端发送的通信请求 """
    # message['user_id']
    # socketio.emit('user_response', {'data': users_to_json}, namespace='/websocket/user_refresh')
    # with thread_lock:
    #     if thread != None:
    #         socketio.start_background_task(target=background_thread,args=(message,))

    user_id = message['user_id']
    if user_id in conns.keys():
        sid = conns[user_id]
        socketio.emit('get_msg',data='asdasd',room=sid,namespace='/websocket/user_refresh')
        print('======='*10)
    print('**id**'*10,message)

