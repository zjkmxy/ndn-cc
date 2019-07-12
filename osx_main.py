import pystray
import os
import signal
from PIL import Image
from sys import platform, argv
from app import app_main


def normal_main():
    child_pid = os.fork()
    if child_pid == 0:
        program_path = os.path.join(os.getcwd(), "..", "MacOS", "NDNCC")
        if os.path.exists(program_path):
            # Run in MacOS application
            os.execl(program_path, program_path, "background")
        elif os.path.exists(os.path.join(os.getcwd(), "venv")):
            # Run in python venv
            program_path = os.path.join(os.getcwd(), "venv", "bin", "python")
            os.execl(program_path, program_path, "./app.py")
        else:
            # Run in default python
            os.execlp("python3", "python3", "./app.py")
    else:
        def sudo_execute(cmd):
            if platform == "darwin":
                script_text = 'do shell script "{}" with administrator privileges'.format(cmd)
                os.spawnlp(os.P_NOWAIT, 'osascript', 'osascript', '-e', script_text)
            else:
                os.spawnlp(os.P_NOWAIT, 'gksudo', 'gksudo', cmd)

        def setup(ico):
            ico.visible = True

        def shutdown(ico):
            os.kill(child_pid, signal.SIGTERM)
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

        icon.run(setup)


if __name__ == '__main__':
    if len(argv) > 1 and argv[1] == "background":
        app_main()
    else:
        normal_main()
