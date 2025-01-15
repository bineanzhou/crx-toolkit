@echo off
REM Download CRX file from URL
if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

python -m crx_toolkit.cli download --url "%~1" --output "%~2"
goto :eof

:usage
echo Usage: download_crx.bat "<url>" "<output_dir>"
echo Example: download_crx.bat "https://example.com/extension.crx" "C:\output"
exit /b 1 