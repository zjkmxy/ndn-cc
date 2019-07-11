from app import app_main
import pystray
import os
import signal
from PIL import Image


if __name__ == '__main__':
    child_pid = os.fork()
    if child_pid == 0:
        app_main()
    else:
        def setup(ico):
            ico.visible = True

        def shutdown(ico):
            os.kill(child_pid, signal.SIGTERM)
            ico.stop()

        def show(_ico):
            os.spawnlp(os.P_NOWAIT, 'open', 'open', 'http://localhost:5000/')
        menu = pystray.Menu(
            pystray.MenuItem('Show', show),
            pystray.MenuItem('Exit', shutdown),
        )

        icon = pystray.Icon('ndncc', menu=menu)
        img = Image.open('ndn_app.png')
        icon.icon = img

        icon.run(setup)
