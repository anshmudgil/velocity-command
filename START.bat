@echo off
echo.
echo  VELOCITY COMMAND
echo  Starting server on http://localhost:4242
echo.
start "" "http://localhost:4242"
C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe "%~dp0serve.py"
pause
