import threading
import asyncio
import subprocess
from ndncc.server import Server
from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO
from ndncc.asyncndn import fetch_data_packet, decode_dict, decode_list, decode_name
from pyndn import Interest, Data
from ndncc.nfd_face_mgmt_pb2 import GeneralStatus, FaceStatusMessage, RibStatusMessage
from pyndn.encoding import ProtobufTlv

# Serve static content from /assets
app = Flask(__name__,
            static_url_path='/static',
            static_folder='static')

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
def index():
    return render_template('index.html')


@app.route('/general-status')
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
@app.route('/exec/add-face', methods=['POST'])
def exec_addface():
    uri = request.form['ip']
    ret = run_until_complete(server.add_face(uri))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return redirect(url_for('face_list', st_code=ret['st_code'], st_text=ret['st_text']))

@app.route('/exec/remove-face', methods=['POST'])
def exec_removeface():
    face_id = int(request.form['face_id'])
    ret = run_until_complete(server.remove_face(face_id))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return redirect(url_for('face_list', st_code=ret['st_code'], st_text=ret['st_text']))

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
        fields_collapse = [field for field in set(fields) - {'face_id', 'uri'}]
        return render_template('face-list.html', face_list=face_list, 
                               fields_collapse=fields_collapse, **request.args.to_dict())
    else:
        print("No response: face-list")
        return "NFD is not running"

@app.route('/face-events')
def face_events():
    return render_template('face-events.html')


### Route
@app.route('/exec/add-route', methods=['POST'])
def exec_addroute():
    name = request.form['name']
    face_id = int(request.form['face_id'])
    ret = run_until_complete(server.add_route(name, face_id))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return redirect(url_for('route_list', st_code=ret['st_code'], st_text=ret['st_text']))

@app.route('/exec/remove-route', methods=['POST'])
def exec_removeroute():
    name = request.form['name']
    face_id = int(request.form['face_id'])
    ret = run_until_complete(server.remove_route(name, face_id))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return redirect(url_for('route_list', st_code=ret['st_code'], st_text=ret['st_text']))

@app.route('/route-list')
def route_list():
    def decode_route_list(msg):
        ret = []
        for item in msg:
            name = decode_name(item.name)
            routes = decode_list(item.route)
            ret.append((name, routes))
        return ret

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
        rib_list = decode_route_list(msg.rib_entry)
        return render_template('route-list.html', rib_list=rib_list, **request.args.to_dict())
    else:
        print("No response: route-list")
        return "NFD is not running"


### Others
@app.route('/auto-configuration')
def auto_configuration():
    return render_template('auto-configuration.html')


@app.route('/exec/autoconf')
def exec_autoconf():
    ret, msg = run_until_complete(server.autoconf())
    return render_template('auto-configuration.html', msg=msg)


@app.route('/certificate-request')
def certificate_request():
    return render_template('certificate-request.html')


@app.route('/key-management')
def key_management():
    key_tree = server.list_key_tree()
    print(key_tree)
    return render_template('key-management.html', key_tree=key_tree)


@app.route('/ndnsec-delete')
def ndnsec_delete():
    name = request.args.get('name', None)
    kind = request.args.get('type', 'n')
    if name is not None:
        ret = subprocess.getoutput('ndnsec-delete -{} "{}"'.format(kind, name))
        return ret


@app.route('/ndnsec-keygen')
def ndnsec_keygen():
    name = request.args.get('name', None)
    if name is not None:
        _ = subprocess.getoutput('ndnsec-keygen -n "{}"'.format(name))
        return redirect(url_for('key_management'))


if __name__ == '__main__':
    socketio.run(app)
