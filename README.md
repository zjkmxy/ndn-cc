Dependencies
============
- Python 3.6
- NodeJS (optional)

Setup Development Environment
=============================
Python venv:
```bash
python3 -m venv ./venv
./venv/bin/python -m pip install -r requirements.txt
```

Electron:
```bash
npm install
```

Execute
=======
Electron:
```bash
npm start
```

Python server:
```bash
./venv/bin/python app.py
```

Generate OSX App
================
To generate a OSX Application, Pillow needs to be compiled from source.
```bash
git clone --branch 6.1.0 https://github.com/python-pillow/Pillow.git
cd Pillow
sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
LDFLAGS=”-headerpad_max_install_names” python setup.py install
```
And then use `py2app`.
```bash
. venv/bin/activate
python setup.py py2app
```
This application needs to be codesigned manually.
