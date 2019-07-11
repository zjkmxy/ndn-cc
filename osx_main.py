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
        def sudo_execute(cmd):
            script_text = 'do shell script "{}" with administrator privileges'.format(cmd)
            os.spawnlp(os.P_NOWAIT, 'osascript', 'osascript', '-e', script_text)

        def setup(ico):
            ico.visible = True

        def shutdown(ico):
            os.kill(child_pid, signal.SIGTERM)
            ico.stop()

        def show(_ico):
            os.spawnlp(os.P_NOWAIT, 'open', 'open', 'http://localhost:5000/')

        def nfd_start(_ico):
            sudo_execute('nfd-start')

        def nfd_stop(_ico):
            sudo_execute('nfd-stop')

        menu = pystray.Menu(
            pystray.MenuItem('Show', show),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('NFD Start', nfd_start),
            pystray.MenuItem('NFD Stop', nfd_stop),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', shutdown),
        )

        icon = pystray.Icon('ndncc', menu=menu)
        img = Image.open('ndn_app.png')
        icon.icon = img

        icon.run(setup)
