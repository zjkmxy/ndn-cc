import asyncio
import threading
from typing import Union
from pyndn import Face, Interest, NetworkNack, Data


async def fetch_data_packet(face: Face, interest: Interest) -> Union[Data, NetworkNack, None]:
    done = threading.Event()
    result = None

    def on_data(_interest, data: Data):
        nonlocal done, result
        result = data
        done.set()

    def on_timeout(_interest):
        nonlocal done
        done.set()

    def on_network_nack(_interest, network_nack: NetworkNack):
        nonlocal done, result
        result = network_nack
        done.set()

    async def wait_for_event():
        ret = False
        while not ret:
            ret = done.wait(0.01)
            await asyncio.sleep(0.01)

    face.expressInterest(interest, on_data, on_timeout, on_network_nack)
    await wait_for_event()
    return result


def decode_dict(msg) -> dict:
    """
    Recursive decode ProtoBuf-type objects
    TODO: Xinyu, is this recursion correct?
    """
    ret = {}
    for field in msg.DESCRIPTOR.fields:
        if field.label == field.LABEL_REPEATED:
            ret[field.name] = decode_list(getattr(msg, field.name))
        elif field.type == field.TYPE_MESSAGE:
            ret[field.name] = decode_dict(getattr(msg, field.name))
        elif (field.type == field.TYPE_UINT32 or field.type == field.TYPE_UINT64):
            ret[field.name] = str(getattr(msg, field.name))
        elif field.type == field.TYPE_BYTES:
            ret[field.name] = getattr(msg, field.name).decode('utf-8')
    return ret

def decode_list(lst) -> list:
    """
    Recursively decode ProtoBuf containers. Because Protobuf Scalar Containers will 
    decode to python primitive types, need to process separately
    """
    ret = []
    for item in lst:
        if isinstance(item, (int, float, str, bool, bytes)):
            ret.append(item)
        else:
            ret.append(decode_dict(item))
    return ret