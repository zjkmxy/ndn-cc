from pyndn import Face, Interest, Data, Name
from pyndn.security import KeyChain
from pyndn.encoding import ProtobufTlv
from .asyncndn import fetch_data_packet
from .nfd_face_mgmt_pb2 import FaceEventNotificationMessage
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

    @staticmethod
    def run_server(work_loop, emit_func):
        asyncio.set_event_loop(work_loop)
        try:
            server = Server(emit_func)
            work_loop.run_until_complete(server.run())
        finally:
            work_loop.close()
