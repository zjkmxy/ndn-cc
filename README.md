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
```bash
. venv/bin.activate
python setup.py py2app
```
This application needs to be codesigned manually.
