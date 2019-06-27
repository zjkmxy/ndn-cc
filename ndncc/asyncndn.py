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
    ret = {}
    for field in msg.DESCRIPTOR.fields:
        if field.type == field.TYPE_MESSAGE:
            pass
        elif (field.type == field.TYPE_UINT32 or
              field.type == field.TYPE_UINT64):
            ret[field.name] = str(getattr(msg, field.name))
        elif field.type == field.TYPE_BYTES:
            ret[field.name] = getattr(msg, field.name).decode('utf-8')
    return ret


def decode_list(lst) -> list:
    ret = []
    for item in lst:
        ret.append(decode_dict(item))
    return ret
