import pystray
import os
from PIL import Image
from sys import platform
from app import app_main
from threading import Thread


def normal_main():
    def sudo_execute(cmd):
        if platform == "darwin":
            script_text = 'do shell script "{}" with administrator privileges'.format(cmd)
            os.spawnlp(os.P_NOWAIT, 'osascript', 'osascript', '-e', script_text)
        else:
            os.spawnlp(os.P_NOWAIT, 'pkexec', 'pkexec', cmd)

    def setup(ico):
        ico.visible = True

    def shutdown(ico):
        ico.stop()

    def show(_ico):
        if platform == "darwin":
            os.spawnlp(os.P_NOWAIT, 'open', 'open', 'http://localhost:5000/')
        else:
            os.spawnlp(os.P_NOWAIT, 'xdg-open', 'xdg-open', 'http://localhost:5000/')

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

    app_thread = Thread(target=app_main)
    app_thread.daemon = True
    app_thread.start()

    icon.run(setup)


if __name__ == '__main__':
    normal_main()
