@echo off
setlocal
if not exist "%~dp0ZeroLink.exe" (
 echo Place this script next to ZeroLink.exe first.
 pause
 exit /b 1
)
mkdir "%LOCALAPPDATA%\ZeroLink" 2>nul
copy /Y "%~dp0ZeroLink.exe" "%LOCALAPPDATA%\ZeroLink\ZeroLink.exe" >nul || exit /b 1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v ZeroLink /t REG_SZ /d "\"%LOCALAPPDATA%\ZeroLink\ZeroLink.exe\"" /f
echo Installed startup entry. Launch ZeroLink.exe now or sign in again.
pause
