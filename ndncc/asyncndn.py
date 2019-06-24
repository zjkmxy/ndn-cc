import asyncio
from typing import Union
from pyndn import Face, Interest, NetworkNack, Data


async def fetch_data_packet(face: Face, interest: Interest) -> Union[Data, NetworkNack, None]:
    done = asyncio.Event()
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

    face.expressInterest(interest, on_data, on_timeout, on_network_nack)
    await done.wait()
    return result
