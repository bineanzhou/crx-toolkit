@echo off
setlocal EnableDelayedExpansion

REM Check arguments
if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

REM Setup virtual environment
python scripts\venv_manager.py
if errorlevel 1 (
    echo Error setting up virtual environment
    exit /b 1
)

REM Get virtual environment Python path
for /f "tokens=*" %%i in ('python -c "from scripts.venv_manager import get_venv_python; print(get_venv_python())"') do set VENV_PYTHON=%%i

REM Handle URL with special characters
set "URL=%~1"

REM Escape special characters in URL
set "URL=!URL:&=^&!"

REM Call Python script with the escaped URL
call "!VENV_PYTHON!" -m crx_toolkit.cli download --url="%URL%" --output="%~2"
if errorlevel 1 (
    echo Error occurred while downloading extension
    exit /b 1
)

echo Successfully downloaded extension
exit /b 0

:usage
echo Usage: download_crx.bat "<url>" "<output_dir>"
echo Examples:
echo   download_crx.bat "https://chromewebstore.google.com/detail/extension-name/extension-id" "output"
echo   download_crx.bat "https://example.com/extension.crx" "output"
echo Note: Always wrap the URL in quotes, special characters like & are supported
exit /b 1 