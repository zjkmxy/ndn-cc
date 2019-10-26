import asyncio
import io
import time
import os
import logging
from typing import Dict
from datetime import datetime
from ndncc.server import Server
from flask import Flask, redirect, render_template, request, url_for, send_file
from flask_socketio import SocketIO
from gevent.event import AsyncResult
from ndn.encoding import is_binary_str, Name, Component
from ndn.types import InterestCanceled, InterestTimeout, InterestNack, ValidationFailure
from ndn.app_support.nfd_mgmt import GeneralStatus, FaceStatusMsg, RibStatus, StrategyChoiceMsg


def decode_dict(msg) -> Dict[str, str]:
    ret = msg.asdict()
    for k, v in ret.items():
        if is_binary_str(v):
            ret[k] = bytes(v).decode()
        else:
            ret[k] = str(v)
    return ret


def app_main():
    from gevent.monkey import patch_all
    patch_all(ssl=False)

    logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        style='{')

    base_path = os.getcwd()
    # Serve static content from /static
    app = Flask(__name__,
                static_url_path='/static',
                static_folder=os.path.join(base_path, 'static'),
                template_folder=os.path.join(base_path, 'templates'))

    app.config['SECRET_KEY'] = '3mlf4j8um6mg2-qlhyzk4ngxxk$8t4hh&$r)%968koxd3i(j#f'
    # socketio = SocketIO(app, async_mode='gevent')
    socketio = SocketIO(app, async_mode='threading')
    server = Server.start_server(socketio.emit)
    last_ping_data = b''

    def run_until_complete(event):
        done = AsyncResult()

        async def run_event():
            nonlocal done
            done.set(await event)

        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().create_task(run_event())
        return done.get()

    @app.route('/')
    def index():
        nfd_state = server.connection_test()
        return render_template('index.html', refer_name='/', nfd_state=nfd_state)

    @app.route('/general-status')
    def general_status():
        def convert_time(timestamp):
            ret = datetime.fromtimestamp(float(timestamp) / 1000.0)
            return str(ret)

        name = "/localhost/nfd/status/general"
        try:
            _, _, data = run_until_complete(server.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True))
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure):
            logging.info("No response: general status")
            return redirect('/')
        msg = GeneralStatus.parse(data)
        status = decode_dict(msg)
        status['start_timestamp'] = convert_time(status['start_timestamp'])
        status['current_timestamp'] = convert_time(status['current_timestamp'])
        return render_template('general-status.html', refer_name='/general-status', name=name, status=status)

    @app.route('/exec/add-face', methods=['POST'])
    def exec_addface():
        if not server.connection_test():
            return redirect('/')

        uri = request.form['ip']
        ret = run_until_complete(server.add_face(uri))
        if ret is None:
            logging.info("No response: add face")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Add face %s %s %s", uri, ret['status_code'], ret['status_text'])
        return redirect(url_for('face_list', st_code=ret['status_code'], st_text=ret['status_text']))

    @app.route('/exec/remove-face', methods=['POST'])
    def exec_removeface():
        if not server.connection_test():
            return redirect('/')

        face_id = int(request.form['face_id'])
        ret = run_until_complete(server.remove_face(face_id))
        if ret is None:
            logging.info("No response: remove face")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Remove face %s %s %s", face_id, ret['status_code'], ret['status_text'])
        return redirect(url_for('face_list', st_code=ret['status_code'], st_text=ret['status_text']))

    @app.route('/face-list')
    def face_list():
        def decode_to_str(dic):
            for k, v in dic.items():
                if isinstance(v, bytes):
                    dic[k] = v.decode()
            return dic

        name = "/localhost/nfd/faces/list"
        try:
            _, _, data = run_until_complete(server.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True))
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure):
            logging.info("No response: face-list")
            return redirect('/')
        msg = FaceStatusMsg.parse(data)
        face_list = [decode_to_str(fs.asdict()) for fs in msg.face_status]
        fields = list(face_list[0].keys())
        fields_collapse = [field for field in set(fields) - {'face_id', 'uri'}]
        return render_template('face-list.html', refer_name='/face-list', face_list=face_list,
                               fields_collapse=fields_collapse, **request.args.to_dict())

    @app.route('/face-events')
    def face_events():
        return render_template('face-events.html', refer_name='/face-events', event_list=server.event_list)

    @app.route('/exec/add-route', methods=['POST'])
    def exec_addroute():
        if not server.connection_test():
            return redirect('/')

        name = request.form['name']
        try:
            face_id = int(request.form['face_id'])
        except ValueError:
            return redirect(url_for('route_list',
                                    st_code='-1',
                                    st_text='Invalid number {}'.format(request.form['face_id'])))

        ret = run_until_complete(server.add_route(name, face_id))
        if ret is None:
            logging.info("No response: add route")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Add route %s->%s %s %s", name, face_id, ret['status_code'], ret['status_text'])
        return redirect(url_for('route_list', st_code=ret['status_code'], st_text=ret['status_text']))

    @app.route('/exec/remove-route', methods=['POST'])
    def exec_removeroute():
        if not server.connection_test():
            return redirect('/')

        name = request.form['name']
        face_id = int(request.form['face_id'])
        ret = run_until_complete(server.remove_route(name, face_id))
        if ret is None:
            logging.info("No response: remove route")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Remove route %s->%s %s %s", name, face_id, ret['status_code'], rext['status_text'])
        return redirect(url_for('route_list', st_code=ret['status_code'], st_text=ret['status_text']))

    @app.route('/route-list')
    def route_list():
        def decode_route_list(msg):
            ret = []
            for item in msg:
                name = Name.to_str(item['name'])
                routes = item['routes']
                ret.append((name, routes))
            return ret

        name = "/localhost/nfd/rib/list"
        try:
            _, _, data = run_until_complete(server.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True))
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure):
            logging.info("No response: route-list")
            return redirect('/')
        msg = RibStatus.parse(data)
        rib_list = decode_route_list(msg.asdict()['entries'])
        return render_template('route-list.html', refer_name='/route-list',
                               rib_list=rib_list, **request.args.to_dict())

    @app.route('/strategy-list')
    def strategy_list():
        def decode_strategy(msg):
            return [{
                "name": Name.to_str(item.name),
                "strategy": Name.to_str(item.strategy.name),
            } for item in msg]

        name = "/localhost/nfd/strategy-choice/list"
        try:
            _, _, data = run_until_complete(server.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True))
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure):
            logging.info("No response: strategy-list")
            return redirect('/')
        msg = StrategyChoiceMsg.parse(data)
        strategy_list = decode_strategy(msg.strategy_choices)
        return render_template('strategy-list.html',
                               refer_name='/strategy-list',
                               strategy_list=strategy_list,
                               **request.args.to_dict())

    @app.route('/exec/set-strategy', methods=['POST'])
    def exec_set_strategy():
        if not server.connection_test():
            return redirect('/')

        name = request.form['name']
        strategy = request.form['strategy']
        ret = run_until_complete(server.set_strategy(name, strategy))
        if ret is None:
            logging.info("No response: set strategy")
            return redirect(url_for('strategy_list', st_code='-1', st_text='No response'))
        else:
            logging.info("Set strategy %s->%s %s %s", name, strategy, ret['status_code'], ret['status_text'])
            return redirect(url_for('strategy_list', st_code=ret['status_code'], st_text=ret['status_text']))

    @app.route('/exec/unset-strategy', methods=['POST'])
    def exec_unset_strategy():
        if not server.connection_test():
            return redirect('/')

        name = request.form['name']
        ret = run_until_complete(server.unset_strategy(name))
        if ret is None:
            logging.info("No response: unset strategy")
            return redirect(url_for('strategy_list', st_code='-1', st_text='No response'))
        else:
            logging.info("Unset strategy %s %s %s", name, ret['status_code'], ret['status_text'])
            return redirect(url_for('strategy_list', st_code=ret['status_code'], st_text=ret['status_text']))

    @app.route('/auto-configuration')
    def auto_configuration():
        return render_template('auto-configuration.html',
                               refer_name='/auto-configuration',
                               **request.args.to_dict())

    @app.route('/exec/autoconf')
    def exec_autoconf():
        if not server.connection_test():
            return redirect('/')

        ret, msg = run_until_complete(server.autoconf())
        return redirect(url_for('auto_configuration', msg=msg))

    @app.route('/certificate-request')
    def certificate_request():
        return render_template('certificate-request.html', refer_name='/certificate-request')

    @app.route('/key-management')
    def key_management():
        key_tree = server.list_key_tree()
        return render_template('key-management.html', refer_name='/key-management', key_tree=key_tree)

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
        return render_template('ndn-ping.html', refer_name='/ndn-ping', **request.args.to_dict())

    @app.route('/exec/ndn-ping', methods=['POST'])
    def exec_ndn_ping():
        def decode_nack_reason(reason) -> str:
            codeset = {0: 'NONE', 50: 'CONGESTION', 100: 'DUPLICATE', 150: 'NO_ROUTE'}
            if reason in codeset:
                return codeset[reason]
            else:
                return str(reason)

        def decode_content_type(content_type) -> str:
            codeset = ["BLOB", "LINK", "KEY", "NACK"]
            if content_type <= 3:
                return codeset[content_type]
            else:
                return str(content_type)

        def decode_signature_type(signature_type) -> str:
            codeset = ["DIGEST_SHA256", "SHA256_WITH_RSA", "SHA256_WITH_ECDSA", "HMAC_WITH_SHA256"]
            if signature_type <= 3:
                return codeset[signature_type]
            else:
                return str(content_type)

        signature_type = None

        async def validator(_, sig):
            nonlocal signature_type
            signature_type = sig.signature_info.signature_type
            return True

        nonlocal last_ping_data
        name = request.form['name']
        can_be_prefix = request.form['can_be_prefix'] == 'true'
        must_be_fresh = request.form['must_be_fresh'] == 'true'
        try:
            interest_lifetime = float(request.form['interest_lifetime']) * 1000.0
        except ValueError:
            interest_lifetime = 4000.0

        st_time = time.time()
        try:
            data_name, meta_info, data = run_until_complete(server.app.express_interest(
                name,
                validator=validator,
                lifetime=int(interest_lifetime),
                can_be_prefix=can_be_prefix,
                must_be_fresh=must_be_fresh))
            ed_time = time.time()
            response_time = '{:.3f}s'.format(ed_time - st_time)
            response_type = 'Data'
            name = Name.to_str(data_name)
            if meta_info.content_type is not None:
                content_type = decode_content_type(meta_info.content_type)
            else:
                content_type = "None"
            if meta_info.freshness_period is not None:
                freshness_period = "{:.3f}s".format(meta_info.freshness_period / 1000.0)
            else:
                freshness_period = "None"
            if meta_info.final_block_id is not None:
                final_block_id = Component.to_str(meta_info.final_block_id)
            else:
                final_block_id = "None"
            if signature_type:
                signature_type = decode_signature_type(signature_type)
            else:
                signature_type = "None"
            last_ping_data = bytes(data)
            return redirect(url_for('ndn_ping',
                                    response_time=response_time,
                                    response_type=response_type,
                                    name=name,
                                    content_type=content_type,
                                    freshness_period=freshness_period,
                                    final_block_id=final_block_id,
                                    signature_type=signature_type,
                                    download='/download/ping-data'))
        except (InterestCanceled, ValidationFailure):
            logging.info("No response: ndn-peek")
            return redirect('/')
        except InterestNack as nack:
            ed_time = time.time()
            response_time = '{:.3f}s'.format(ed_time - st_time)
            response_type = 'NetworkNack'
            reason = decode_nack_reason(nack.reason)
            return redirect(url_for('ndn_ping',
                                    response_time=response_time,
                                    response_type=response_type,
                                    name=name,
                                    reason=reason))
        except InterestTimeout:
            ed_time = time.time()
            response_time = '{:.3f}s'.format(ed_time - st_time)
            response_type = 'Timeout'
            return redirect(url_for('ndn_ping',
                                    response_time=response_time,
                                    response_type=response_type,
                                    name=name))

    @app.route('/download/ping-data')
    def download_ping_data():
        return send_file(
            io.BytesIO(last_ping_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            attachment_filename='ping.data'
            )

    socketio.run(app)


if __name__ == '__main__':
    app_main()
