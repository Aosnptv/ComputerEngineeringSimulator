@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
set "PROJECT_DIR=%CD%"
set "OUTPUT_DIR=%PROJECT_DIR%\builds\windows"
set "PACKAGE_DIR=%PROJECT_DIR%\builds\package"
set "ZIP_PATH=%PROJECT_DIR%\builds\ComputerEngineeringVR-Windows-x64.zip"

if defined GODOT_EXE if exist "%GODOT_EXE%" goto :godot_ready
where godot >nul 2>nul
if errorlevel 1 where godot4 >nul 2>nul
if errorlevel 1 (
  echo ERROR: Godot 4.7.2 stable was not found on PATH.
  echo Install Godot 4.7.2 stable and matching Windows export templates.
  exit /b 2
)
for /f "delims=" %%G in ('where godot 2^>nul') do set "GODOT=%%G" & goto :found
for /f "delims=" %%G in ('where godot4 2^>nul') do set "GODOT=%%G" & goto :found
:found
set "GODOT_EXE=%GODOT%"
:godot_ready
if not exist "%PROJECT_DIR%\project.godot" exit /b 3
if not exist "%PROJECT_DIR%\tests\validate_project.py" exit /b 3

python "%PROJECT_DIR%\tests\validate_project.py"
if errorlevel 1 exit /b 4
"%GODOT_EXE%" --headless --xr-mode off --path "%PROJECT_DIR%" --editor --quit
if errorlevel 1 exit /b 5
"%GODOT_EXE%" --headless --xr-mode off --path "%PROJECT_DIR%" --script "%PROJECT_DIR%\tests\headless_suite.gd"
if errorlevel 1 exit /b 5
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
"%GODOT_EXE%" --headless --xr-mode off --path "%PROJECT_DIR%" --export-release "Windows Desktop" "%OUTPUT_DIR%\ComputerEngineeringVR.exe"
if errorlevel 1 exit /b 6
if not exist "%OUTPUT_DIR%\ComputerEngineeringVR.exe" exit /b 7

if exist "%PACKAGE_DIR%" rmdir /s /q "%PACKAGE_DIR%"
mkdir "%PACKAGE_DIR%\LICENSES"
copy /y "%OUTPUT_DIR%\ComputerEngineeringVR.exe" "%PACKAGE_DIR%\" >nul
if exist "%OUTPUT_DIR%\ComputerEngineeringVR.pck" copy /y "%OUTPUT_DIR%\ComputerEngineeringVR.pck" "%PACKAGE_DIR%\" >nul
copy /y "%PROJECT_DIR%\README_PLAY.txt" "%PACKAGE_DIR%\" >nul
copy /y "%PROJECT_DIR%\docs\ASSET_CREDITS.md" "%PACKAGE_DIR%\LICENSES\ASSET_CREDITS.txt" >nul
tar.exe -a -c -f "%ZIP_PATH%" -C "%PACKAGE_DIR%" .
if errorlevel 1 exit /b 8
if not exist "%ZIP_PATH%" exit /b 9
echo Build complete: %ZIP_PATH%
exit /b 0

