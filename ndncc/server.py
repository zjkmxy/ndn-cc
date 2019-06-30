from pyndn import Face, Interest, Data, Name
from pyndn.security import KeyChain
from pyndn.encoding import ProtobufTlv
from .asyncndn import fetch_data_packet
from .nfd_face_mgmt_pb2 import FaceEventNotificationMessage, ControlCommandMessage, ControlResponseMessage
import asyncio


class Server:
    def __init__(self, emit_func):
        self.emit = emit_func
        self.running = True

        self.face = Face()
        self.keychain = KeyChain()
        self.face.setCommandSigningInfo(self.keychain, self.keychain.getDefaultCertificateName())

    async def run(self):
        face_event = asyncio.get_event_loop().create_task(self.face_event())
        while self.running:
            self.face.processEvents()
            await asyncio.sleep(0.01)
        await face_event

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
        while self.running:
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
            face_interest.interestLifetimeMilliseconds = 60000

            ret = await fetch_data_packet(self.face, face_interest)
            if isinstance(ret, Data):
                last_seq = ret.name[-1].toSequenceNumber()
                face_event = FaceEventNotificationMessage()
                try:
                    ProtobufTlv.decode(face_event, ret.content)

                    dic = self.face_event_to_dict(face_event.face_event_notification)
                    self.emit('face event', dic)
                except RuntimeError as exc:
                    print('Decode failed', exc)
                    last_seq = -1
            else:
                print("No response")
                last_seq = -1

            await asyncio.sleep(0.1)

    async def add_face(self, uri):
        if uri[-1] == "/":
            uri = uri[:-1]
        if uri.find("://") < 0:
            uri = "udp4://" + uri
        if len(uri.split(":")) < 3:
            uri = uri + ":6363"

        interest = self.make_command('faces', 'create', uri=uri)
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

    async def add_route(self, name: str, face_id: int):
        interest = self.make_command('rib', 'register',
                                     name=Name(name),
                                     face_id=face_id)
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

    def run_server(self, work_loop):
        asyncio.set_event_loop(work_loop)
        try:
            work_loop.run_until_complete(self.run())
        finally:
            work_loop.close()

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
                cmd_param.control_parameters.strategy.component.append(compo.getValue().toBytes())
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
