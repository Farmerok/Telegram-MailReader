echo off

pyinstaller --clean --hidden-import=pyttsx3.drivers --hidden-import=pyttsx3.drivers.sapi5 --onefile -d noarchive --noconsole --icon icons.ico checkmail.py

del /s /q /f checkmail.spec
rmdir /s /q __pycache__
rmdir /s /q build

:cmd
pause null