import threading
import asyncio
from ndncc.server import Server
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = '3mlf4j8um6mg2-qlhyzk4ngxxk$8t4hh&$r)%968koxd3i(j#f'
socketio = SocketIO(app)

work_loop = asyncio.new_event_loop()
thread = threading.Thread(target=Server.run_server, args=(work_loop, socketio.emit))
thread.setDaemon(True)
thread.start()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/faceevents')
def index():
    return render_template('faceevents.html')


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
