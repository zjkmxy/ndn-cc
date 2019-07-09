import threading
import asyncio
import subprocess
import time
from datetime import datetime
from ndncc.server import Server
from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO
from ndncc.asyncndn import fetch_data_packet, decode_dict, decode_list, decode_name, \
    decode_content_type, decode_nack_reason
from pyndn import Interest, Data, NetworkNack
from ndncc.nfd_face_mgmt_pb2 import GeneralStatus, FaceStatusMessage, RibStatusMessage, \
    StrategyChoiceMessage
from pyndn.encoding import ProtobufTlv

# Serve static content from /static
app = Flask(__name__,
            static_url_path='/static',
            static_folder='static')

app.config['SECRET_KEY'] = '3mlf4j8um6mg2-qlhyzk4ngxxk$8t4hh&$r)%968koxd3i(j#f'
socketio = SocketIO(app)
server = Server.start_server(socketio.emit)


def run_until_complete(event):
    asyncio.set_event_loop(asyncio.new_event_loop())
    return asyncio.get_event_loop().run_until_complete(event)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/general-status')
def general_status():
    def convert_time(timestamp):
        ret = datetime.fromtimestamp(float(timestamp) / 1000.0)
        return str(ret)

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
            return "Decoding Error"
        status = decode_dict(msg)
        status['start_timestamp'] = convert_time(status['start_timestamp'])
        status['current_timestamp'] = convert_time(status['current_timestamp'])
        return render_template('general-status.html', name=name, status=status)
    else:
        print("No response")
        return "NFD is not running"


### Face
@app.route('/exec/add-face', methods=['POST'])
def exec_addface():
    if not server.connection_test():
        return "NFD is not running"

    uri = request.form['ip']
    ret = run_until_complete(server.add_face(uri))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return redirect(url_for('face_list', st_code=ret['st_code'], st_text=ret['st_text']))

@app.route('/exec/remove-face', methods=['POST'])
def exec_removeface():
    if not server.connection_test():
        return "NFD is not running"

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
            return "Decoding Error"
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
    return render_template('face-events.html', event_list=server.event_list)


### Route
@app.route('/exec/add-route', methods=['POST'])
def exec_addroute():
    if not server.connection_test():
        return "NFD is not running"

    name = request.form['name']
    try:
        face_id = int(request.form['face_id'])
    except ValueError:
        return redirect(url_for('route_list',
                                st_code='-1',
                                st_text='Invalid number {}'.format(request.form['face_id'])))

    ret = run_until_complete(server.add_route(name, face_id))
    if ret is None:
        print("No response")
    else:
        print(ret['st_code'], ret['st_text'])
    return redirect(url_for('route_list', st_code=ret['st_code'], st_text=ret['st_text']))

@app.route('/exec/remove-route', methods=['POST'])
def exec_removeroute():
    if not server.connection_test():
        return "NFD is not running"

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
            return "Decoding Error"
        rib_list = decode_route_list(msg.rib_entry)
        return render_template('route-list.html', rib_list=rib_list, **request.args.to_dict())
    else:
        print("No response: route-list")
        return "NFD is not running"


# Strategy
@app.route('/strategy-list')
def strategy_list():
    def decode_strategy(msg):
        return [{
            "name": decode_name(item.name),
            "strategy": decode_name(item.strategy.name),
        } for item in msg]

    interest = Interest("/localhost/nfd/strategy-choice/list")
    interest.mustBeFresh = True
    interest.canBePrefix = True
    ret = run_until_complete(fetch_data_packet(server.face, interest))
    if isinstance(ret, Data):
        msg = StrategyChoiceMessage()
        try:
            ProtobufTlv.decode(msg, ret.content)
        except RuntimeError as exc:
            print("Decoding Error", exc)
            return "Decoding Error"
        strategy_list = decode_strategy(msg.strategy_choice)
        return render_template('strategy-list.html', strategy_list=strategy_list,
                               **request.args.to_dict())
    else:
        print("No response: strategy-list")
        return "NFD is not running"


@app.route('/exec/set-strategy', methods=['POST'])
def exec_set_strategy():
    if not server.connection_test():
        return "NFD is not running"

    name = request.form['name']
    strategy = request.form['strategy']
    ret = run_until_complete(server.set_strategy(name, strategy))
    if ret is None:
        print("No response")
        return redirect(url_for('strategy_list', st_code='-1', st_text='No response'))
    else:
        print(ret['st_code'], ret['st_text'])
        return redirect(url_for('strategy_list', st_code=ret['st_code'], st_text=ret['st_text']))


@app.route('/exec/unset-strategy', methods=['POST'])
def exec_unset_strategy():
    if not server.connection_test():
        return "NFD is not running"

    name = request.form['name']
    ret = run_until_complete(server.unset_strategy(name))
    if ret is None:
        print("No response")
        return redirect(url_for('strategy_list', st_code='-1', st_text='No response'))
    else:
        print(ret['st_code'], ret['st_text'])
        return redirect(url_for('strategy_list', st_code=ret['st_code'], st_text=ret['st_text']))


### Others
@app.route('/auto-configuration')
def auto_configuration():
    return render_template('auto-configuration.html')


@app.route('/exec/autoconf')
def exec_autoconf():
    if not server.connection_test():
        return "NFD is not running"

    ret, msg = run_until_complete(server.autoconf())
    return render_template('auto-configuration.html', msg=msg)


@app.route('/certificate-request')
def certificate_request():
    return render_template('certificate-request.html')


@app.route('/key-management')
def key_management():
    key_tree = server.list_key_tree()
    return render_template('key-management.html', key_tree=key_tree)


@app.route('/ndnsec-delete')
def ndnsec_delete():
    name = request.args.get('name', None)
    kind = request.args.get('type', 'n')
    if name is not None:
        server.delete_security_object(name, kind)
        time.sleep(0.1)
        return redirect(url_for('key_management'))


@app.route('/ndnsec-keygen')
def ndnsec_keygen():
    name = request.args.get('name', None)
    if name is not None:
        server.create_identity(name)
        time.sleep(0.1)
        return redirect(url_for('key_management'))


@app.route('/ndn-ping')
def ndn_ping():
    return render_template('ndn-ping.html')


@app.route('/exec/ndn-ping', methods=['POST'])
def exec_ndn_ping():
    name = request.form['name']
    can_be_prefix = request.form['can_be_prefix'] == 'true'
    must_be_fresh = request.form['must_be_fresh'] == 'true'
    try:
        interest_lifetime = float(request.form['interest_lifetime']) * 1000.0
    except ValueError:
        interest_lifetime = 4000.0

    interest = Interest(name)
    interest.canBePrefix = can_be_prefix
    interest.mustBeFresh = must_be_fresh
    interest.interestLifetimeMilliseconds = interest_lifetime
    st_time = time.time()
    ret = run_until_complete(fetch_data_packet(server.face, interest))
    ed_time = time.time()
    response_time = '{:.3f}s'.format(ed_time - st_time)
    if isinstance(ret, Data):
        response_type = 'Data'
        name = ret.name.toUri()
        content_type = decode_content_type(ret.metaInfo.type)
        freshness_period = "{:.3f}s".format(ret.metaInfo.freshnessPeriod / 1000.0)
        final_block_id = ret.metaInfo.finalBlockId.toEscapedString()
        signature_type = type(ret.signature).__name__
        return render_template('ndn-ping.html',
                               response_time=response_time,
                               response_type=response_type,
                               name=name,
                               content_type=content_type,
                               freshness_period=freshness_period,
                               final_block_id=final_block_id,
                               signature_type=signature_type)
    elif isinstance(ret, NetworkNack):
        response_type = 'NetworkNack'
        reason = decode_nack_reason(ret.getReason())
        return render_template('ndn-ping.html',
                               response_time=response_time,
                               response_type=response_type,
                               name=name,
                               reason=reason)
    elif ret is None:
        response_type = 'Timeout'
        return render_template('ndn-ping.html',
                               response_time=response_time,
                               response_type=response_type,
                               name=name)
    else:
        print("No response: ndn-ping")
        return "NFD is not running"


# NFD Management
@app.route('/nfd-management')
def nfd_management():
    nfd_state = server.connection_test()
    return render_template('nfd-management.html', nfd_state=nfd_state)


@app.route('/exec/start-nfd')
def start_nfd():
    subprocess.run('nfd-start')
    return redirect('/nfd-management')


@app.route('/exec/stop-nfd')
def stop_nfd():
    subprocess.run('nfd-stop')
    return redirect('/nfd-management')


if __name__ == '__main__':
    socketio.run(app)
