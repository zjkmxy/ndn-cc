import threading
from pyndn import Face, Interest, Data, Name
from pyndn.security import KeyChain, Pib
from pyndn.encoding import ProtobufTlv
from pyndn.transport.unix_transport import UnixTransport
from pyndn.security.pib.pib_key import PibKey
from pyndn.security.v2.certificate_v2 import CertificateV2
from .asyncndn import fetch_data_packet
from .nfd_face_mgmt_pb2 import FaceEventNotificationMessage, ControlCommandMessage,\
    ControlResponseMessage, FaceQueryFilterMessage, FaceStatusMessage
import asyncio
import urllib.request
import socket


class Server:
    def __init__(self, emit_func):
        self.emit = emit_func
        self.running = True
        self.event_list = []

        # 1. If you use default constructor, when NFD is not started,
        # TcpTransport will be used instead of UnixTransport.
        # 2. Both TcpTransport and UnixTransport are not connected
        # before the first Interest is sent.
        # file_path = Face._getUnixSocketFilePathForLocalhost()
        # transport = UnixTransport()
        # connection_info = UnixTransport.ConnectionInfo(file_path)
        # self.face = Face(transport, connection_info)

        self.keychain = KeyChain()
        self.face = None

    def start_reconnection(self):
        """
        Start reconnection process.
        NOT thread safe.
        """
        self.face.shutdown()
        self.face = None

    def get_or_create_certificate(self):
        id_name = Name('/ndncc')
        cur_id = self.keychain.createIdentityV2(id_name)
        return cur_id.getDefaultKey().getDefaultCertificate().name

    def connection_test(self):
        interest = Interest("/localhost/nfd/faces/events")
        interest.mustBeFresh = True
        interest.canBePrefix = True
        interest.interestLifetimeMilliseconds = 1000
        try:
            def empty(*_args, **_kwargs):
                pass

            self.face.expressInterest(interest, empty, empty, empty)
            return True
        except (ConnectionRefusedError, BrokenPipeError, OSError):
            return False

    async def run(self):
        while self.running:
            print("Restarting face...")
            self.face = Face()
            self.face.setCommandSigningInfo(self.keychain, self.get_or_create_certificate())
            if self.connection_test():
                print("Succeeded")
                face_event = asyncio.get_event_loop().create_task(self.face_event())
                while self.running and self.face is not None:
                    try:
                        self.face.processEvents()
                    except AttributeError:
                        print("Attribute error.")
                        self.start_reconnection()
                    await asyncio.sleep(0.01)
                await face_event
            else:
                print("Failed")
            await asyncio.sleep(3)

    @staticmethod
    def face_event_to_dict(msg):
        ret = {}
        if msg.face_event_kind == 1:
            ret['face_event_kind'] = "CREATED"
        elif msg.face_event_kind == 2:
            ret['face_event_kind'] = "DESTROYED"
        elif msg.face_event_kind == 3:
            ret['face_event_kind'] = "UP"
        elif msg.face_event_kind == 4:
            ret['face_event_kind'] = "DOWN"
        else:
            ret['face_event_kind'] = "unknown"

        ret['face_id'] = str(msg.face_id)
        ret['local_uri'] = msg.local_uri.decode("utf-8")
        ret['remote_uri'] = msg.uri.decode("utf-8")

        if msg.face_scope == 1:
            ret['face_scope'] = "local"
        else:
            ret['face_scope'] = "non-local"

        if msg.face_persistency == 0:
            ret['face_persistency'] = "persistent"
        elif msg.face_event_kind == 1:
            ret['face_persistency'] = "on-demand"
        elif msg.face_persistency == 2:
            ret['face_persistency'] = "permanent"
        else:
            ret['face_persistency'] = "unknown"

        if msg.link_type == 0:
            ret['link_type'] = "point-to-point"
        elif msg.link_type == 1:
            ret['link_type'] = "multi-access"
        elif msg.link_type == 2:
            ret['link_type'] = "ad-hoc"
        else:
            ret['link_type'] = "unknown"

        ret['flags'] = str(msg.flags)
        return ret

    @staticmethod
    def response_to_dict(msg):
        ret = {'st_code': msg.st_code, 'st_text': msg.st_text.decode('utf-8')}
        return ret

    async def face_event(self):
        last_seq = -1
        retry_time = 3000
        retry_count_limit = 60000 // retry_time
        retry_count = 0
        while self.running and self.face:
            name = Name("/localhost/nfd/faces/events")
            face_interest = Interest()
            if last_seq >= 0:
                name.appendSequenceNumber(last_seq + 1)
                face_interest.canBePrefix = False
            else:
                face_interest.mustBeFresh = True
                face_interest.canBePrefix = True
            print(name.toUri())
            face_interest.name = name
            # face_interest.interestLifetimeMilliseconds = 60000
            face_interest.interestLifetimeMilliseconds = retry_time

            ret = await fetch_data_packet(self.face, face_interest)

            if isinstance(ret, Data):
                retry_count = 0
                last_seq = ret.name[-1].toSequenceNumber()
                face_event = FaceEventNotificationMessage()
                try:
                    ProtobufTlv.decode(face_event, ret.content)

                    dic = self.face_event_to_dict(face_event.face_event_notification)
                    dic['seq'] = str(last_seq)
                    self.emit('face event', dic)
                    self.event_list.append(dic)
                except RuntimeError as exc:
                    print('Decode failed', exc)
                    last_seq = -1
            elif ret is None:
                if retry_count >= retry_count_limit:
                    print("No response")
                    last_seq = -1
                    retry_count = 0
                else:
                    retry_count += 1
            else:
                print("NFD is not running: start reconnection")
                self.start_reconnection()
                return

            await asyncio.sleep(0.1)

    async def issue_command_interest(self, interest):
        ret = await fetch_data_packet(self.face, interest)
        if isinstance(ret, Data):
            response = ControlResponseMessage()
            try:
                ProtobufTlv.decode(response, ret.content)

                dic = self.response_to_dict(response.control_response)
                print(dic)
                return dic
            except RuntimeError as exc:
                print('Decode failed', exc)
        return None

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

        interest = self.make_command('faces', 'create', uri=uri)
        return await self.issue_command_interest(interest)
    
    async def remove_face(self, face_id: int):
        interest = self.make_command('faces', 'destroy', face_id=face_id)
        return await self.issue_command_interest(interest)

    async def add_route(self, name: str, face_id: int):
        interest = self.make_command('rib', 'register',
                                     name=Name(name), face_id=face_id)
        return await self.issue_command_interest(interest)

    async def remove_route(self, name: str, face_id: int):
        interest = self.make_command('rib', 'unregister', 
                                     name=Name(name), face_id=face_id)
        return await self.issue_command_interest(interest)

    async def set_strategy(self, name: str, strategy: str):
        interest = self.make_command('strategy-choice', 'set',
                                     name=Name(name), strategy=Name(strategy))
        return await self.issue_command_interest(interest)

    async def unset_strategy(self, name: str):
        interest = self.make_command('strategy-choice', 'unset', name=Name(name))
        return await self.issue_command_interest(interest)

    def run_server(self, work_loop):
        asyncio.set_event_loop(work_loop)
        try:
            work_loop.run_until_complete(self.run())
        finally:
            work_loop.close()

    @staticmethod
    def start_server(emit_func):
        done = threading.Event()
        server = None

        def create_and_run():
            nonlocal server, done
            server = Server(emit_func)
            work_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(work_loop)
            done.set()
            try:
                work_loop.run_until_complete(server.run())
            finally:
                work_loop.close()

        thread = threading.Thread(target=create_and_run)
        thread.setDaemon(True)
        thread.start()
        done.wait()
        return server

    def make_command(self, module, verb, **kwargs):
        name = Name('/localhost/nfd').append(module).append(verb)

        # Command Parameters
        cmd_param = ControlCommandMessage()
        if 'name' in kwargs:
            name_param = kwargs['name']
            for compo in name_param:
                cmd_param.control_parameters.name.component.append(compo.getValue().toBytes())
        if 'strategy' in kwargs:
            name_param = kwargs['strategy']
            for compo in name_param:
                cmd_param.control_parameters.strategy.name.component.append(compo.getValue().toBytes())
        for key in ['uri', 'local_uri']:
            if key in kwargs:
                setattr(cmd_param.control_parameters, key, kwargs[key].encode('utf-8'))
        for key in ['face_id', 'origin', 'cost', 'capacity', 'count', 'base_cong_mark', 'def_cong_thres',
                    'mtu', 'flags', 'mask', 'exp_period']:
            if key in kwargs:
                setattr(cmd_param.control_parameters, key, kwargs[key])
        param_blob = ProtobufTlv.encode(cmd_param)
        name.append(Name.Component(param_blob))

        # Command Interest Components
        ret = Interest(name)
        ret.canBePrefix = True
        self.face.makeCommandInterest(ret)

        return ret

    @staticmethod
    def list_key_tree():
        """
        Return the id-key-cert tree in a JSON like dict object.
        """
        pib = KeyChain().getPib()
        identities = pib._identities._identityNames
        ret = {}
        try:
            default_id = pib.getDefaultIdentity().getName()
        except Pib.Error:
            default_id = Name('/')
        for id_name in identities:
            id_obj = pib.getIdentity(Name(id_name))
            cur_id = {'default': '*' if id_name == default_id else ' '}
            try:
                default_key = id_obj.getDefaultKey().getName()
            except Pib.Error:
                default_key = Name('/')

            keys = id_obj._getKeys()._keyNames
            cur_id['keys'] = {}
            for key_name in keys:
                key_obj = id_obj.getKey(Name(key_name))
                cur_key = {'default': '*' if key_name == default_key else ' '}
                try:
                    default_cert = key_obj.getDefaultCertificate().getName()
                except Pib.Error:
                    default_cert = Name('/')

                key_type = key_obj.getKeyType()
                if key_type <= 4:
                    cur_key['key_type'] = ['NONE', 'RSA', 'EC', 'AES', 'HMAC'][key_type]
                else:
                    cur_key['key_type'] = 'unknown'

                certs = key_obj._getCertificates()._certificateNames
                cur_key['certs'] = {}
                for cert_name in certs:
                    cert_obj = key_obj.getCertificate(Name(cert_name))
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
        key_chain = KeyChain()
        try:
            cur_id = key_chain.getPib().getIdentity(Name(name))
            key_chain.createKey(cur_id)
        except Pib.Error:
            key_chain.createIdentityV2(Name(name))

    @staticmethod
    def delete_security_object(name, kind):
        key_chain = KeyChain()
        print(name, kind)
        if kind == "c":
            id_name = CertificateV2.extractIdentityFromCertName(Name(name))
            key_name = CertificateV2.extractKeyNameFromCertName(Name(name))
            cur_id = key_chain.getPib().getIdentity(id_name)
            cur_key = cur_id.getKey(key_name)
            key_chain.deleteCertificate(cur_key, Name(name))
        elif kind == "k":
            id_name = PibKey.extractIdentityFromKeyName(Name(name))
            cur_id = key_chain.getPib().getIdentity(id_name)
            cur_key = cur_id.getKey(Name(name))
            key_chain.deleteKey(cur_id, cur_key)
        else:
            key_chain.deleteIdentity(Name(name))

    async def query_face_id(self, uri):
        query_filter = FaceQueryFilterMessage()
        query_filter.face_query_filter.uri = uri.encode('utf-8')
        query_filter_msg = ProtobufTlv.encode(query_filter)
        name = Name("/localhost/nfd/faces/query").append(Name.Component(query_filter_msg))
        interest = Interest(name)
        interest.mustBeFresh = True
        interest.canBePrefix = True
        ret = await fetch_data_packet(self.face, interest)
        if not isinstance(ret, Data):
            return None
        msg = FaceStatusMessage()
        try:
            ProtobufTlv.decode(msg, ret.content)
        except RuntimeError as exc:
            print("Decoding Error", exc)
            return None
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

        interest = self.make_command('faces', 'create', uri=uri)
        ret = await fetch_data_packet(self.face, interest)
        if not isinstance(ret, Data):
            return False, "Create face failed"
        response = ControlResponseMessage()
        try:
            ProtobufTlv.decode(response, ret.content)
        except RuntimeError as exc:
            print('Decode failed', exc)
            return False, "Create face failed"

        # # Ignore duplicated face
        # if response.control_response.st_code not in {200, 409}:
        #     return False, "Create face failed"

        face_id = await self.query_face_id(uri)
        if face_id is None:
            return False, "Create face failed"

        route = Name("/ndn")
        interest = self.make_command('rib', 'register', name=route, face_id=face_id, origin=66, cost=100)
        await fetch_data_packet(self.face, interest)

        route = Name("/localhop/nfd")
        interest = self.make_command('rib', 'register', name=route, face_id=face_id, origin=66, cost=100)
        await fetch_data_packet(self.face, interest)

        return True, "Auto-configuration finished"
