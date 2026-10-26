@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo Requesting optional SteamVR/OpenXR mode.
echo If the runtime, headset, or Python backend is unavailable, the game will
echo report the missing component and continue safely in desktop mode.
echo.

call "%~dp0run.bat" --vr %*
exit /b %ERRORLEVEL%

