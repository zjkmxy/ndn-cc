import threading
import asyncio
from ndncc.server import Server
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from ndncc.asyncndn import fetch_data_packet, decode_dict, decode_list
from pyndn import Interest, Data
from ndncc.nfd_face_mgmt_pb2 import GeneralStatus, FaceStatusMessage, RibStatusMessage
from pyndn.encoding import ProtobufTlv

# Serve static content from /assets
app = Flask(__name__,
            static_url_path='',
            static_folder='assets')

app.config['SECRET_KEY'] = '3mlf4j8um6mg2-qlhyzk4ngxxk$8t4hh&$r)%968koxd3i(j#f'
socketio = SocketIO(app)

work_loop = asyncio.new_event_loop()
server = Server(socketio.emit)
thread = threading.Thread(target=server.run_server, args=(work_loop,))
thread.setDaemon(True)
thread.start()


def run_until_complete(event):
    asyncio.set_event_loop(asyncio.new_event_loop())
    return asyncio.get_event_loop().run_until_complete(event)


@app.route('/')
def general_status():
    interest = Interest("/localhost/nfd/status/general")
    interest.mustBeFresh = True
    interest.canBePrefix = True
    ret = run_until_complete(fetch_data_packet(server.face, interest))
    if isinstance(ret, Data):
        name = ret.name.toUri()
        msg = GeneralStatus()
        try:
            ProtobufTlv.decode(msg, ret.content)
        except RuntimeError as exc:
            print("Decoding Error", exc)
            return "NFD is not running"
        status = decode_dict(msg)
        return render_template('general-status.html', name=name, status=status)
    else:
        print("No response")
        return "NFD is not running"


### Face
@app.route('/add-face')
def add_face():
    return render_template('add-face.html')

@app.route('/exec/add-face', methods=['POST'])
def exec_addface():
    uri = request.form['ip']
    ret = run_until_complete(server.add_face(uri))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return render_template('add-face.html', **ret)

@app.route('/face-list')
def face_list():
    interest = Interest("/localhost/nfd/faces/list")
    interest.mustBeFresh = True
    interest.canBePrefix = True
    ret = run_until_complete(fetch_data_packet(server.face, interest))
    if isinstance(ret, Data):
        name = ret.name.toUri()
        msg = FaceStatusMessage()
        try:
            ProtobufTlv.decode(msg, ret.content)
        except RuntimeError as exc:
            print("Decoding Error", exc)
            return "NFD is not running"
        face_list = decode_list(msg.face_status)
        fields = list(face_list[0].keys())
        return render_template('face-list.html', fields=fields, face_list=face_list)
    else:
        print("No response: face-list")
        return "NFD is not running"

@app.route('/face-events')
def face_events():
    return render_template('face-events.html')

# TODO: Remove face?


### Route
@app.route('/add-route')
def add_route():
    return render_template('add-route.html')

@app.route('/exec/add-route', methods=['POST'])
def exec_addroute():
    name = request.form['name']
    face_id = int(request.form['face_id'])
    ret = run_until_complete(server.add_route(name, face_id))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return render_template('add-route.html', **ret)


@app.route('/route-list')
def route_list():
    interest = Interest("/localhost/nfd/rib/list")
    interest.mustBeFresh = True
    interest.canBePrefix = True
    ret = run_until_complete(fetch_data_packet(server.face, interest))
    if isinstance(ret, Data):
        name = ret.name.toUri()
        msg = RibStatusMessage()
        try:
            ProtobufTlv.decode(msg, ret.content)
        except RuntimeError as exc:
            print("Decoding Error", exc)
            return "NFD is not running"
        rib_list = decode_list(msg.rib_entry)
        fields = list(rib_list[0].keys())
        return render_template('route-list.html', fields=fields, rib_list=rib_list)
    else:
        print("No response: route-list")
        return "NFD is not running"

    return render_template('route-list.html')


### Others
@app.route('/auto-configuration')
def auto_configuration():
    return render_template('auto-configuration.html')

@app.route('/certificate-request')
def certificate_request():
    return render_template('certificate-request.html')

@app.route('/key-management')
def key_management():
    return render_template('key-management.html')



@socketio.on('connect')
def face_event_socket():
    print("CONNECTED")


@socketio.on('my event')
def face_event_socket(json):
    print("MY EVENT" + str(json))


if __name__ == '__main__':
    socketio.run(app)
