import asyncio
import urllib.request
import socket
import logging
from enum import Enum, Flag
from aiohttp import web
from datetime import datetime
from Cryptodome.PublicKey import RSA, ECC
from ndn.app import NDNApp
from ndn.encoding import Name, Component, SignatureType
from ndn.types import InterestCanceled, InterestTimeout, InterestNack, ValidationFailure, NetworkError
from ndn.app_support.nfd_mgmt import FaceEventNotification, parse_response, make_command,\
    FaceQueryFilter, FaceQueryFilterValue, FaceStatusMsg, FibStatus, RibStatus
from ndn.app_support.security_v2 import parse_certificate


class Server:
    def __init__(self, emit_func):
        self.emit = emit_func
        self.running = True
        self.event_list = []
        self.app = NDNApp()

    def start_reconnection(self):
        """
        Start reconnection process.
        NOT thread safe.
        """
        self.app.shutdown()

    def connection_test(self):
        return self.app.face.running

    @staticmethod
    def decode_to_str(dic):
        for k, v in dic.items():
            if isinstance(v, bytes):
                dic[k] = v.decode()
            elif isinstance(v, Enum):
                dic[k] = v.name
            elif isinstance(v, Flag):
                s = str(v)
                dic[k] = s.split('.')[1]
            elif k == 'name':
                dic[k] = Name.to_str(v)
            elif k == 'routes':
                dic[k] = [Server.decode_to_str(r) for r in v]
        return dic

    async def run(self):
        logging.info("Restarting app...")
        while True:
            try:
                await self.app.main_loop(self.face_event())
            except KeyboardInterrupt:
                logging.info('Receiving Ctrl+C, shutdown')
                break
            except (FileNotFoundError, ConnectionRefusedError):
                logging.info("NFD disconnected...")
            finally:
                self.app.shutdown()
            await asyncio.sleep(3.0)

    async def fetch_list(self, module_name: str):
        name = "/localhost/nfd/" + module_name
        try:
            _, _, data = await self.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True)
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure, NetworkError):
            logging.info("No response: " + module_name)
            raise web.HTTPFound('/')
        return data

    async def get_face_list(self):
        msg = FaceStatusMsg.parse(await self.fetch_list('faces/list'))
        face_list = [self.decode_to_str(fs.asdict()) for fs in msg.face_status]
        return face_list

    async def get_fib_list(self):
        msg = FibStatus.parse(await self.fetch_list('fib/list'))
        fib_list = [self.decode_to_str(ent.asdict()) for ent in msg.entries]
        return fib_list

    async def get_rib_list(self):
        msg = RibStatus.parse(await self.fetch_list('rib/list'))
        rib_list = [self.decode_to_str(ent.asdict()) for ent in msg.entries]
        return rib_list

    async def face_event(self):
        last_seq = -1
        name_prefix = Name.from_str('/localhost/nfd/faces/events')
        while True:
            if last_seq >= 0:
                name = name_prefix + [Component.from_sequence_num(last_seq + 1)]
                init = False
            else:
                name = name_prefix
                init = True
            logging.info("Face event notification stream %s", Name.to_str(name))
            try:
                data_name, _, content = await self.app.express_interest(
                    name, must_be_fresh=init, can_be_prefix=init, lifetime=60000)
                last_seq = Component.to_number(data_name[-1])
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if not content:
                    print('ERROR: Face event is empty')
                elif content[0] == 0x65:
                    msg = parse_response(content)
                    print('Query failed with response', msg['status_code'], msg['status_text'])
                else:
                    dic = self.face_event_to_dict(content)
                    dic['seq'] = str(last_seq)
                    dic['time'] = timestamp
                    await self.emit('face event', dic)
                    self.event_list.append(dic)
            except (InterestCanceled, NetworkError):
                break
            except InterestTimeout:
                last_seq = -1
            except InterestNack as e:
                print(f'Face events nacked with reason={e.reason}')
                last_seq = -1
            except ValidationFailure:
                print('Face events failed to validate')
                last_seq = -1
            await asyncio.sleep(0.1)

    @staticmethod
    def face_event_to_dict(msg):
        ret = {}
        event = FaceEventNotification.parse(msg)

        ret['face_event_kind'] = event.event.face_event_kind.name
        ret['face_id'] = str(event.event.face_id)
        ret['local_uri'] = event.event.local_uri
        ret['remote_uri'] = event.event.uri
        ret['face_scope'] = event.event.face_scope.name
        ret['face_persistency'] = event.event.face_persistency.name
        ret['link_type'] = event.event.link_type.name
        ret['flags'] = str(event.event.flags)[10:]  # Remove 'FaceFlags.'
        return ret

    async def issue_command_interest(self, cmd):
        try:
            logging.info('Issuing command %s', Name.to_str(cmd))
            _, _, data = await self.app.express_interest(
                cmd, lifetime=1000, can_be_prefix=True, must_be_fresh=True)
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure, NetworkError):
            logging.error(f'Command failed')
            return None
        return parse_response(data)

    async def add_face(self, uri):
        # It's not easy to distinguish udp4://127.0.0.1 and udp4://spurs.cs.ucla.edu
        # if reduce(lambda a, b: a or b, (x.isalpha() for x in uri)):
        #     uri = socket.gethostbyname(uri)
        if uri[-1] == "/":
            uri = uri[:-1]
        if uri.find("://") < 0:
            uri = "udp4://" + uri
        if len(uri.split(":")) < 3:
            uri = uri + ":6363"

        interest = make_command('faces', 'create', uri=uri.encode())
        return await self.issue_command_interest(interest)

    async def remove_face(self, face_id: int):
        interest = make_command('faces', 'destroy', face_id=face_id)
        return await self.issue_command_interest(interest)

    async def add_route(self, name: str, face_id: int):
        interest = make_command('rib', 'register', name=name, face_id=face_id)
        return await self.issue_command_interest(interest)

    async def remove_route(self, name: str, face_id: int):
        interest = make_command('rib', 'unregister', name=name, face_id=face_id)
        return await self.issue_command_interest(interest)

    async def set_strategy(self, name: str, strategy: str):
        interest = make_command('strategy-choice', 'set', name=name, strategy=strategy)
        return await self.issue_command_interest(interest)

    async def unset_strategy(self, name: str):
        interest = make_command('strategy-choice', 'unset', name=name)
        return await self.issue_command_interest(interest)

    def list_key_tree(self):
        """
        Return the id-key-cert tree in a JSON like dict object.
        """
        def get_key_type(key):
            key = bytes(key)
            try:
                RSA.import_key(key)
                return 'RSA'
            except ValueError:
                pass
            try:
                ECC.import_key(key)
                return 'ECC'
            except ValueError:
                pass
            return 'Unknown'
        sig_type_dic = {
            SignatureType.NOT_SIGNED: 'NotSigned',
            SignatureType.DIGEST_SHA256: 'DigestSha256',
            SignatureType.SHA256_WITH_RSA: 'SignatureSha256WithRsa',
            SignatureType.SHA256_WITH_ECDSA: 'SignatureSha256WithEcdsa',
            SignatureType.HMAC_WITH_SHA256: 'SignatureHmacWithSha256'
        }

        pib = self.app.keychain
        ret = {}
        for id_name, id_obj in pib.items():
            cur_id = {'default': '*' if id_obj.is_default else ' ', 'keys': {}}
            for key_name, key_obj in id_obj.items():
                cur_key = {
                    'default': '*' if key_obj.is_default else ' ',
                    'key_type': get_key_type(key_obj.key_bits),
                    'certs': {}
                }
                for cert_name, cert_obj in key_obj.items():
                    cert_v2 = parse_certificate(cert_obj.data)
                    cur_cert = {
                        'default': '*' if cert_obj.is_default else ' ',
                        'not_before': bytes(cert_v2.signature_info.validity_period.not_before).decode(),
                        'not_after': bytes(cert_v2.signature_info.validity_period.not_after).decode(),
                        'issuer_id': Component.to_str(cert_v2.name[-2]),
                        'key_locator': Name.to_str(cert_v2.signature_info.key_locator.name),
                        'signature_type': sig_type_dic.get(cert_v2.signature_info.signature_type, 'Unknown')
                    }
                    cur_key['certs'][Name.to_str(cert_name)] = cur_cert
                cur_id['keys'][Name.to_str(key_name)] = cur_key
            ret[Name.to_str(id_name)] = cur_id
        return ret

    def create_identity(self, name):
        if name in self.app.keychain:
            self.app.keychain.new_key(name)
        else:
            self.app.keychain.new_identity(name)

    def delete_security_object(self, name, kind):
        keychain = self.app.keychain
        if kind == "c":
            keychain.del_cert(name)
        elif kind == "k":
            keychain.del_key(name)
        else:
            keychain.del_identity(name)

    async def query_face_id(self, uri):
        query_filter = FaceQueryFilter()
        query_filter.face_query_filter = FaceQueryFilterValue()
        query_filter.face_query_filter.uri = uri
        query_filter_msg = query_filter.encode()
        name = Name.from_str("/localhost/nfd/faces/query") + [Component.from_bytes(query_filter_msg)]
        try:
            _, _, data = await self.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True)
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure, NetworkError):
            logging.error(f'Query failed')
            return None
        msg = FaceStatusMsg.parse(data)
        if len(msg.face_status) <= 0:
            return None
        return msg.face_status[0].face_id

    async def autoconf(self):
        """
        Automatically connect to ndn testbed.
        Add route /ndn and /localhop/nfd.
        """
        uri = urllib.request.urlopen("http://ndn-fch.named-data.net/").read().decode('utf-8')
        uri = socket.gethostbyname(uri)
        uri = "udp4://" + uri + ":6363"

        cmd = make_command('faces', 'create', uri=uri)
        ret = await self.issue_command_interest(cmd)
        if not isinstance(ret, dict):
            return False, "Create face failed"

        face_id = await self.query_face_id(uri)
        if face_id is None:
            return False, "Create face failed"

        route = '/ndn'
        cmd = make_command('rib', 'register', name=route, face_id=face_id, origin=66, cost=100)
        await self.issue_command_interest(cmd)
        route = '/localhop/nfd'
        cmd = make_command('rib', 'register', name=route, face_id=face_id, origin=66, cost=100)
        await self.issue_command_interest(cmd)

        return True, "Auto-configuration finished"
