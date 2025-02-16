@echo off
setlocal EnableDelayedExpansion

REM 获取脚本所在目录的绝对路径
set "SCRIPT_DIR=%~dp0"

REM 检查 Python 环境
python3 --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required but not installed.
    exit /b 1
)

REM 检查 PIL 库
python3 -c "from PIL import Image" >nul 2>&1
if errorlevel 1 (
    echo Error: Python Pillow library is required but not installed.
    echo Please install it using: pip install Pillow
    exit /b 1
)

REM 显示帮助信息
:show_help
if "%~1"=="" goto :help
if "%~2"=="" goto :help
goto :main

:help
echo 用法: crx_convert_icon ^<源图片^> ^<扩展目录^>
echo.
echo 将图片转换为 Chrome 扩展所需的各种尺寸的图标
echo.
echo 参数说明:
echo   源图片         源图片文件路径
echo   扩展目录       Chrome 扩展目录路径
echo.
echo 示例:
echo   crx_convert_icon logo.png my-extension                  # 使用相对路径
echo   crx_convert_icon C:\path\to\icon.png C:\path\to\extension    # 使用绝对路径
echo   crx_convert_icon .\assets\icon.jpg .\extension           # 支持 JPG 格式
echo   crx_convert_icon ..\resources\logo.png .\chrome-ext      # 使用上级目录的图片
exit /b 1

:main
REM 运行 Python 脚本
python3 -c "from crx_toolkit.crx_icon_converter import convert_crx_icon; convert_crx_icon()" "%~1" "%~2"
if errorlevel 1 (
    exit /b 1
)

exit /b 0