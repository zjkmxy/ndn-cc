import asyncio
import time
import os
import logging
from enum import Enum, Flag
from typing import Dict
from datetime import datetime
from aiohttp import web
import socketio
import aiohttp_jinja2
import jinja2
from ndncc.server import Server
from ndn.encoding import is_binary_str, Name, Component
from ndn.types import InterestCanceled, InterestTimeout, InterestNack, ValidationFailure, NetworkError
from ndn.app_support.nfd_mgmt import GeneralStatus, FaceStatusMsg, RibStatus, FibStatus, StrategyChoiceMsg


def decode_dict(msg) -> Dict[str, str]:
    ret = msg.asdict()
    for k, v in ret.items():
        if is_binary_str(v):
            ret[k] = bytes(v).decode()
        elif isinstance(v, Enum):
            ret[k] = v.name
        elif isinstance(v, Flag):
            s = str(v)
            ret[k] = s.split('.')[1]
        else:
            ret[k] = str(v)
    return ret


def app_main(main_thread=False):
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    logging.basicConfig(format='[{asctime}]{levelname}:{message}',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.WARNING,
                        style='{')

    base_path = os.getcwd()
    # Serve static content from /static
    sio = socketio.AsyncServer(async_mode='aiohttp')
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(base_path, 'templates')))
    sio.attach(app)
    app.router.add_static(prefix='/static', path=os.path.join(base_path, 'static'))
    routeTable = web.RouteTableDef()
    # app = Flask(__name__,
    #             static_url_path='/static',
    #             static_folder=os.path.join(base_path, 'static'),
    #             template_folder=os.path.join(base_path, 'templates'))

    # app.config['SECRET_KEY'] = '3mlf4j8um6mg2-qlhyzk4ngxxk$8t4hh&$r)%968koxd3i(j#f'
    # socketio = SocketIO(app, async_mode='gevent')
    # socketio = SocketIO(app, async_mode='threading')
    # server = Server.start_server(sio.emit)
    server = Server(sio.emit)
    last_ping_data = b''

    def render_template(template_name, request, **kwargs):
        return aiohttp_jinja2.render_template(template_name, request, context=kwargs)

    def redirect(route_name, request, **kwargs):
        raise web.HTTPFound(request.app.router[route_name].url_for().with_query(kwargs))

    @routeTable.get('/')
    async def index(request):
        nfd_state = server.connection_test()
        return render_template('index.html', request, refer_name='/', nfd_state=nfd_state)

    @routeTable.get('/forwarder-status')
    async def forwarder_status(request):
        def convert_time(timestamp):
            ret = datetime.fromtimestamp(float(timestamp) / 1000.0)
            return str(ret)

        name = "/localhost/nfd/status/general"
        try:
            _, _, data = await server.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True)
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure, NetworkError):
            logging.info("No response: forwarder status")
            raise web.HTTPFound('/')
        msg = GeneralStatus.parse(data)
        status = decode_dict(msg)
        status['start_timestamp'] = convert_time(status['start_timestamp'])
        status['current_timestamp'] = convert_time(status['current_timestamp'])
        return render_template('forwarder-status.html', request, refer_name='/forwarder-status', name=name, status=status)

    @routeTable.post('/faces/add')
    async def faces_add(request):
        if not server.connection_test():
            raise web.HTTPFound('/')

        form = await request.post()
        uri = form['ip']
        ret = await server.add_face(uri)
        if ret is None:
            logging.info("No response: add face")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Added face %s %s %s", uri, ret['status_code'], ret['status_text'])
        return redirect('faces', request, st_code=ret['status_code'], st_text=ret['status_text'])

    @routeTable.post('/faces/remove')
    async def faces_remove(request):
        if not server.connection_test():
            raise web.HTTPFound('/')

        form = await request.post()
        face_id = int(form['face_id'])
        ret = await server.remove_face(face_id)
        if ret is None:
            logging.info("No response: remove face")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Removed face %s %s %s", face_id, ret['status_code'], ret['status_text'])
        return redirect('faces', request, st_code=ret['status_code'], st_text=ret['status_text'])

    @routeTable.get('/faces', name='faces')
    async def faces(request):
        face_list = await server.get_face_list()
        fields = list(face_list[0].keys())
        fields_collapse = [field for field in set(fields) - {'face_id', 'uri'}]
        face_data = None
        if 'face_id' in request.query:
            for f in face_list:
                if str(f['face_id']) == request.query['face_id']:
                    face_data = f
                    break
        route_data = []
        if face_data is not None:
            fib = await server.get_fib_list()
            for fe in fib:
                for nh in fe['next_hop_records']:
                    if str(nh['face_id']) == request.query['face_id']:
                        route_data.append({'route': fe['name'], 'cost': nh['cost']})
        return render_template('faces.html', request, refer_name='/faces', face_list=face_list,
                               fields_collapse=fields_collapse, face_data=face_data,
                               route_data=route_data,
                               **request.query)

    @routeTable.get('/face-events')
    async def face_events(request):
        return render_template('face-events.html', request, refer_name='/face-events', event_list=server.event_list)

    @routeTable.post('/routing/add')
    async def routing_add(request):
        if not server.connection_test():
            raise web.HTTPFound('/')

        form = await request.post()
        name = form['name']
        try:
            face_id = int(form['face_id'])
        except ValueError:
            return redirect('routing', request, st_code='-1', st_text=f'Invalid number {form["face_id"]}')

        ret = await server.add_route(name, face_id)
        if ret is None:
            logging.info("No response: add route")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Added route %s->%s %s %s", name, face_id, ret['status_code'], ret['status_text'])
        return redirect('routing', request, st_code=ret['status_code'], st_text=ret['status_text'])

    @routeTable.post('/routing/remove')
    async def routing_remove(request):
        if not server.connection_test():
            raise web.HTTPFound('/')

        form = await request.post()
        name = form['name']
        face_id = int(form['face_id'])
        ret = await server.remove_route(name, face_id)
        if ret is None:
            logging.info("No response: remove route")
            ret = {'status_code': -1, 'status_text': 'No response'}
        else:
            logging.info("Removed route %s->%s %s %s", name, face_id, ret['status_code'], ret['status_text'])
        return redirect('routing', request, st_code=ret['status_code'], st_text=ret['status_text'])

    @routeTable.get('/routing', name='routing')
    async def routing(request):
        # Get list of faces to map FaceIds to FaceUris
        face_list = await server.get_face_list()
        face_map = {}
        for face in face_list:
            face_map[face['face_id']] = face['uri']
        fib_list = await server.get_fib_list()
        rib_list = await server.get_rib_list()

        fib_routes = []
        rib_routes = []
        request_name = None
        if 'name' in request.query:
            request_name = request.query['name']
            for ent in fib_list:
                if ent['name'] == request_name:
                    fib_routes = ent['next_hop_records']
                    break
            for ent in rib_list:
                if ent['name'] == request_name:
                    rib_routes = ent['routes']
                    break

        return render_template('routing.html', request, refer_name='/routing',
                               rib_list=rib_list, fib_list=fib_list, face_map=face_map,
                               fib_routes=fib_routes, rib_routes=rib_routes, request_name=request_name,
                               **request.query)

    @routeTable.get('/strategies', name='strategies')
    async def strategies(request):
        def decode_strategy(msg):
            return [{
                "name": Name.to_str(item.name),
                "strategy": Name.to_str(item.strategy.name),
            } for item in msg]

        name = "/localhost/nfd/strategy-choice/list"
        try:
            _, _, data = await server.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True)
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure, NetworkError):
            logging.info("No response: strategy-list")
            raise web.HTTPFound('/')
        msg = StrategyChoiceMsg.parse(data)
        strategy_list = decode_strategy(msg.strategy_choices)
        return render_template('strategies.html',
                               request,
                               refer_name='/strategies',
                               strategy_list=strategy_list,
                               **request.query)

    @routeTable.post('/strategies/set')
    async def strategies_set(request):
        if not server.connection_test():
            raise web.HTTPFound('/')

        form = await request.post()
        name = form['name']
        strategy = form['strategy']
        ret = await server.set_strategy(name, strategy)
        if ret is None:
            logging.info("No response: set strategy")
            return redirect('strategies', request, st_code='-1', st_text='No response')
        else:
            logging.info("Set strategy %s->%s %s %s", name, strategy, ret['status_code'], ret['status_text'])
            return redirect('strategies', request, st_code=ret['status_code'], st_text=ret['status_text'])

    @routeTable.post('/strategies/unset')
    async def strategies_unset(request):
        if not server.connection_test():
            raise web.HTTPFound('/')

        form = await request.post()
        name = form['name']
        ret = await server.unset_strategy(name)
        if ret is None:
            logging.info("No response: unset strategy")
            return redirect('strategies', request, st_code='-1', st_text='No response')
        else:
            logging.info("Unset strategy %s %s %s", name, ret['status_code'], ret['status_text'])
            return redirect('strategies', request, st_code=ret['status_code'], st_text=ret['status_text'])

    @routeTable.get('/autoconf', name='autoconf')
    async def autoconf(request):
        return render_template('autoconf.html',
                               request,
                               refer_name='/autoconf',
                               **request.query)

    @routeTable.get('/autoconf/perform')
    async def autoconf_perform(request):
        if not server.connection_test():
            raise web.HTTPFound('/')

        ret, msg = await server.autoconf()
        return redirect('autoconf', request, msg=msg)

    @routeTable.get('/certificate-requests')
    async def certificate_requests(request):
        return render_template('certificate-requests.html', request, refer_name='/certificate-requests')

    @routeTable.get('/key-management', name='key_management')
    async def key_management(request):
        key_tree = server.list_key_tree()
        return render_template('key-management.html', request, refer_name='/key-management', key_tree=key_tree)

    @routeTable.get('/ndnsec-delete')
    async def ndnsec_delete(request):
        args = request.query
        name = args.get('name', None)
        kind = args.get('type', 'n')
        if name is not None:
            server.delete_security_object(name, kind)
            time.sleep(0.1)
            return redirect('key_management', request)

    @routeTable.get('/ndnsec-keygen')
    async def ndnsec_keygen(request):
        args = request.query
        name = args.get('name', None)
        if name is not None:
            server.create_identity(name)
            time.sleep(0.1)
            return redirect('key_management', request)

    @routeTable.get('/ndn-ping', name='ndn_ping')
    async def ndn_ping(request):
        return render_template('ndn-ping.html', request, refer_name='/ndn-ping', **request.query)

    @routeTable.post('/exec/ndn-ping')
    async def exec_ndn_ping(request):
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
        form = await request.post()
        name = form['name']
        can_be_prefix = form['can_be_prefix'] == 'true'
        must_be_fresh = form['must_be_fresh'] == 'true'
        try:
            interest_lifetime = float(form['interest_lifetime']) * 1000.0
        except ValueError:
            interest_lifetime = 4000.0

        st_time = time.time()
        try:
            data_name, meta_info, data = await server.app.express_interest(
                name,
                validator=validator,
                lifetime=int(interest_lifetime),
                can_be_prefix=can_be_prefix,
                must_be_fresh=must_be_fresh)
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
            return redirect('ndn_ping',
                            request,
                            response_time=response_time,
                            response_type=response_type,
                            name=name,
                            content_type=content_type,
                            freshness_period=freshness_period,
                            final_block_id=final_block_id,
                            signature_type=signature_type,
                            download='/download/ping-data')
        except ValueError as e:
            logging.info("Illegal name")
            return redirect('ndn_ping',
                            request,
                            response_time='ERROR',
                            response_type=str(e),
                            name=name)
        except (InterestCanceled, ValidationFailure, NetworkError):
            logging.info("No response: ndn-peek")
            raise web.HTTPFound('/')
        except InterestNack as nack:
            ed_time = time.time()
            response_time = '{:.3f}s'.format(ed_time - st_time)
            response_type = 'NetworkNack'
            reason = decode_nack_reason(nack.reason)
            return redirect('ndn_ping',
                            request,
                            response_time=response_time,
                            response_type=response_type,
                            name=name,
                            reason=reason)
        except InterestTimeout:
            ed_time = time.time()
            response_time = '{:.3f}s'.format(ed_time - st_time)
            response_type = 'Timeout'
            return redirect('ndn_ping',
                            request,
                            response_time=response_time,
                            response_type=response_type,
                            name=name)

    @routeTable.get('/download/ping-data')
    async def download_ping_data(_request):
        return web.Response(
            body=last_ping_data,
            content_type='application/octet-stream',
            headers={'Content-Disposition': 'attachment; filename="{ping.data}"'})

    app.add_routes(routeTable)
    asyncio.ensure_future(server.run())

    async def run_app():
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 5000)
        await site.start()

    if main_thread:
        web.run_app(app, port=5000)
    else:
        asyncio.get_event_loop().run_until_complete(run_app())
        asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    app_main(True)
