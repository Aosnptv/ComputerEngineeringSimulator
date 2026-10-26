
@echo off
setlocal EnableExtensions
title Computer Engineering Simulator

cd /d "%~dp0"

set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUTF8=1"
set "PYTHONPATH="
set "CES_RESOURCE_DIAGNOSTICS=0"
set "GAME_DIR=%~dp0ComputerEngineeringVR"
set "GAME_MAIN=%GAME_DIR%\src\main.py"
set "PYTHON_EXE="

if not exist "%GAME_MAIN%" (
    echo [ERROR] Game entry point not found:
    echo %GAME_MAIN%
    pause
    exit /b 1
)

echo =========================================
echo    COMPUTER ENGINEERING SIMULATOR
echo =========================================
echo.
echo Searching for Python with Panda3D...
echo.

REM 1. Verified external virtual environment. Keep this outside the repository.
call :check_python "%LOCALAPPDATA%\venvs\ComputerEngineeringSimulator-py312\Scripts\python.exe" "external Python 3.12 environment"
if defined PYTHON_EXE goto launch

REM 2. Other existing environments. The launcher never creates or changes them.
call :check_python "%~dp0.venv\Scripts\python.exe" "repository-root environment"
if defined PYTHON_EXE goto launch

call :check_python "%GAME_DIR%\.venv\Scripts\python.exe" "legacy tracked environment"
if defined PYTHON_EXE goto launch

REM 3. Python 3.12 user installation.
call :check_python "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" "user Python 3.12"
if defined PYTHON_EXE goto launch

REM 4. Python installations on PATH.
for /f "delims=" %%P in ('where python.exe 2^>nul') do (
    if not defined PYTHON_EXE call :check_python "%%P" "Python on PATH"
)
if defined PYTHON_EXE goto launch

echo.
echo [ERROR] No compatible Python with Panda3D found.
echo.
echo Checked virtual environments and Python installations.
echo No files were changed or packages installed.
echo.
echo Required: CPython 3.12 x64 and Panda3D 1.10.16.
pause
exit /b 1

:check_python
if not exist "%~1" (
    echo [SKIP] %~2 not found:
    echo        %~1
    exit /b 0
)

echo [CHECK] %~2
echo         %~1
"%~1" -B -c "import struct,sys,panda3d; from direct.showbase.ShowBase import ShowBase; assert sys.version_info[:2] == (3,12), 'requires Python 3.12'; assert struct.calcsize('P') == 8, 'requires 64-bit Python'; assert panda3d.__version__ == '1.10.16', 'requires Panda3D 1.10.16'; print('[OK] Python', sys.version.split()[0], '64-bit, Panda3D', panda3d.__version__)"

if not errorlevel 1 (
    set "PYTHON_EXE=%~1"
    echo.
) else (
    echo [SKIP] Candidate is not compatible. Error output is shown above.
    echo.
)
exit /b 0

:launch
echo [OK] Compatible Python found:
echo %PYTHON_EXE%
echo.
"%PYTHON_EXE%" -B -c "import sys,panda3d; print('Python executable:', sys.executable); print('Panda3D version:', panda3d.__version__)"
if errorlevel 1 (
    echo.
    echo [ERROR] Python validation changed before startup.
    pause
    exit /b 1
)
echo.
echo Starting game...
echo.

pushd "%GAME_DIR%"
"%PYTHON_EXE%" -B "%GAME_MAIN%" %*
set "EXIT_CODE=%ERRORLEVEL%"
popd

echo.
if not "%EXIT_CODE%"=="0" (
    echo [ERROR] Game exited with code %EXIT_CODE%.
    pause
) else (
    echo Game closed normally.
)

exit /b %EXIT_CODE%
