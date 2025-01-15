@echo off
REM Parse CRX file and display information
if "%~1"=="" goto :usage

python -m crx_toolkit.cli parse --file "%~1"
goto :eof

:usage
echo Usage: parse_crx.bat "<crx_file>"
echo Example: parse_crx.bat "C:\output\extension.crx"
exit /b 1 