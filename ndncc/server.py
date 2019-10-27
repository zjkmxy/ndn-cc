import asyncio
import urllib.request
import socket
import logging
from datetime import datetime
from ndn.app import NDNApp
from ndn.encoding import Name, Component
from ndn.types import InterestCanceled, InterestTimeout, InterestNack, ValidationFailure
from ndn.app_support.nfd_mgmt import FaceEventNotification, parse_response, make_command,\
    FaceQueryFilter, FaceQueryFilterValue, FaceStatusMsg


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

    async def run(self):
        logging.info("Restarting app...")
        while True:
            try:
                await self.app.main_loop(self.face_event())
            except KeyboardInterrupt:
                logging.info('Receiving Ctrl+C, shutdown')
                break
            except FileNotFoundError:
                logging.info("NFD disconnected...")
            finally:
                self.app.shutdown()
            await asyncio.sleep(3.0)

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
                dic = self.face_event_to_dict(content)
                dic['seq'] = str(last_seq)
                dic['time'] = timestamp
                await self.emit('face event', dic)
                self.event_list.append(dic)
            except InterestCanceled:
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
        if event.event.face_event_kind == 1:
            ret['face_event_kind'] = "CREATED"
        elif event.event.face_event_kind == 2:
            ret['face_event_kind'] = "DESTROYED"
        elif event.event.face_event_kind == 3:
            ret['face_event_kind'] = "UP"
        elif event.event.face_event_kind == 4:
            ret['face_event_kind'] = "DOWN"
        else:
            ret['face_event_kind'] = "unknown"

        ret['face_id'] = str(event.event.face_id)
        ret['local_uri'] = bytes(event.event.local_uri).decode("utf-8")
        ret['remote_uri'] = bytes(event.event.uri).decode("utf-8")

        if event.event.face_scope == 1:
            ret['face_scope'] = "local"
        else:
            ret['face_scope'] = "non-local"

        if event.event.face_persistency == 0:
            ret['face_persistency'] = "persistent"
        elif event.event.face_persistency == 1:
            ret['face_persistency'] = "on-demand"
        elif event.event.face_persistency == 2:
            ret['face_persistency'] = "permanent"
        else:
            ret['face_persistency'] = "unknown"

        if event.event.link_type == 0:
            ret['link_type'] = "point-to-point"
        elif event.event.link_type == 1:
            ret['link_type'] = "multi-access"
        elif event.event.link_type == 2:
            ret['link_type'] = "ad-hoc"
        else:
            ret['link_type'] = "unknown"

        ret['flags'] = str(event.event.flags)
        return ret

    async def issue_command_interest(self, cmd):
        try:
            logging.info('Issuing command %s', Name.to_str(cmd))
            _, _, data = await self.app.express_interest(
                cmd, lifetime=1000, can_be_prefix=True, must_be_fresh=True)
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure):
            logging.error(f'Command failed')
            return None
        ret = parse_response(data)
        ret['status_text'] = ret['status_text'].decode()
        return ret

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

    @staticmethod
    def list_key_tree():
        """
        Return the id-key-cert tree in a JSON like dict object.
        """
        return {}
        pib = KeyChain().getPib()
        identities = pib._identities._identityNames
        ret = {}
        try:
            default_id = pib.getDefaultIdentity().getName()
        except Pib.Error:
            default_id = PyName('/')
        for id_name in identities:
            id_obj = pib.getIdentity(PyName(id_name))
            cur_id = {'default': '*' if id_name == default_id else ' '}
            try:
                default_key = id_obj.getDefaultKey().getName()
            except Pib.Error:
                default_key = PyName('/')

            keys = id_obj._getKeys()._keyNames
            cur_id['keys'] = {}
            for key_name in keys:
                key_obj = id_obj.getKey(PyName(key_name))
                cur_key = {'default': '*' if key_name == default_key else ' '}
                try:
                    default_cert = key_obj.getDefaultCertificate().getName()
                except Pib.Error:
                    default_cert = PyName('/')

                key_type = key_obj.getKeyType()
                if key_type <= 4:
                    cur_key['key_type'] = ['NONE', 'RSA', 'EC', 'AES', 'HMAC'][key_type]
                else:
                    cur_key['key_type'] = 'unknown'

                certs = key_obj._getCertificates()._certificateNames
                cur_key['certs'] = {}
                for cert_name in certs:
                    cert_obj = key_obj.getCertificate(PyName(cert_name))
                    signature = cert_obj.getSignature()
                    cur_cert = {
                        'default': '*' if cert_name == default_cert else ' ',
                        'not_before': str(cert_obj.getValidityPeriod().getNotBefore()),
                        'not_after': str(cert_obj.getValidityPeriod().getNotAfter()),
                        'issuer_id': cert_obj.getIssuerId().toEscapedString(),
                        'key_locator': signature.getKeyLocator().getKeyName().toUri(),
                        'signature_type': cert_obj.getSignature().__class__.__name__,
                    }
                    cur_key['certs'][cert_name.toUri()] = cur_cert
                cur_id['keys'][key_name.toUri()] = cur_key
            ret[id_name.toUri()] = cur_id
        return ret

    @staticmethod
    def create_identity(name):
        return
        key_chain = KeyChain()
        try:
            cur_id = key_chain.getPib().getIdentity(PyName(name))
            key_chain.createKey(cur_id)
        except Pib.Error:
            key_chain.createIdentityV2(PyName(name))

    @staticmethod
    def delete_security_object(name, kind):
        return
        key_chain = KeyChain()
        logging.info("Delete security object %s %s", name, kind)
        if kind == "c":
            id_name = CertificateV2.extractIdentityFromCertName(PyName(name))
            key_name = CertificateV2.extractKeyNameFromCertName(PyName(name))
            cur_id = key_chain.getPib().getIdentity(id_name)
            cur_key = cur_id.getKey(key_name)
            key_chain.deleteCertificate(cur_key, PyName(name))
        elif kind == "k":
            id_name = PibKey.extractIdentityFromKeyName(PyName(name))
            cur_id = key_chain.getPib().getIdentity(id_name)
            cur_key = cur_id.getKey(PyName(name))
            key_chain.deleteKey(cur_id, cur_key)
        else:
            key_chain.deleteIdentity(PyName(name))

    async def query_face_id(self, uri):
        query_filter = FaceQueryFilter()
        query_filter.face_query_filter = FaceQueryFilterValue()
        query_filter.face_query_filter.uri = uri.encode('utf-8')
        query_filter_msg = query_filter.encode()
        name = Name.from_str("/localhost/nfd/faces/query") + [Component.from_bytes(query_filter_msg)]
        try:
            _, _, data = await self.app.express_interest(
                name, lifetime=1000, can_be_prefix=True, must_be_fresh=True)
        except (InterestCanceled, InterestTimeout, InterestNack, ValidationFailure):
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

        cmd = make_command('faces', 'create', uri=uri.encode())
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
