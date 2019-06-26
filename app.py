import threading
import asyncio
from ndncc.server import Server
from flask import Flask, render_template, request
from flask_socketio import SocketIO

from pyndn.encoding import ProtobufTlv
from ndncc.nfd_face_mgmt_pb2 import ControlResponseMessage

app = Flask(__name__)
app.config['SECRET_KEY'] = '3mlf4j8um6mg2-qlhyzk4ngxxk$8t4hh&$r)%968koxd3i(j#f'
socketio = SocketIO(app)

work_loop = asyncio.new_event_loop()
server = Server(socketio.emit)
thread = threading.Thread(target=server.run_server, args=(work_loop,))
thread.setDaemon(True)
thread.start()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/faceevents')
def index():
    return render_template('faceevents.html')


@app.route('/add-face')
def addface():
    return render_template('add-face.html')


@app.route('/exec/add-face', methods=['POST'])
def exec_addface():
    uri = request.form['ip']
    asyncio.set_event_loop(asyncio.new_event_loop())
    ret = asyncio.get_event_loop().run_until_complete(server.add_face(uri))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return render_template('add-face.html', **ret)


@app.route('/socket.io.js')
def socket_io_js():
    return render_template('socket.io.js')


@socketio.on('connect')
def face_event_socket():
    print("CONNECTED")


@socketio.on('my event')
def face_event_socket(json):
    print("MY EVENT" + str(json))


if __name__ == '__main__':
    socketio.run(app)
