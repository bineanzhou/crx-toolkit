@echo off
REM Pack Chrome extension into CRX format
if "%~1"=="" goto :usage
if "%~2"=="" goto :usage
if "%~3"=="" goto :usage

python -m crx_toolkit.cli pack --source "%~1" --key "%~2" --output "%~3"
goto :eof

:usage
echo Usage: pack_crx.bat "<extension_dir>" "<private_key>" "<output_dir>"
echo Example: pack_crx.bat "C:\extensions\my_extension" "C:\keys\private.pem" "C:\output"
exit /b 1 