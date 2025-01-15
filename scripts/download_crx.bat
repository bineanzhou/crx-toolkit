@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

REM 设置日志文件
set "LOG_FILE=crx_download.log"

REM 初始化参数默认值
set "URL="
set "OUTPUT_DIR=output"
set "SHOW_HELP="
set "DEBUG="
set "PROXY="
set "FORCE="
set "NO_VERIFY="

REM 记录原始参数
call :log "=== 开始解析参数 ==="
call :log "原始参数列表: %*"

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :check_args

REM 记录当前处理的参数
call :log "处理参数: [%~1]"

REM 如果URL已经设置，则跳过剩余参数
if defined URL (
    call :log_warning "URL已设置，跳过剩余参数: %~1"
    shift
    goto :parse_args
)

REM 处理选项参数
set "_arg=%~1"
if "!_arg:~0,1!" == "-" (
    REM 处理带值的选项
    if /i "!_arg!" == "-o" (
        if "%~2" == "" (
            call :log_error "-o 选项需要一个参数"
            goto :show_help
        )
        set "OUTPUT_DIR=%~2"
        call :log "设置输出目录: !OUTPUT_DIR!"
        shift & shift
        goto :parse_args
    )
    if /i "!_arg!" == "--output" (
        if "%~2" == "" (
            call :log_error "--output 选项需要一个参数"
            goto :show_help
        )
        set "OUTPUT_DIR=%~2"
        call :log "设置输出目录: !OUTPUT_DIR!"
        shift & shift
        goto :parse_args
    )
    if /i "!_arg!" == "-p" (
        if "%~2" == "" (
            call :log_error "-p 选项需要一个参数"
            goto :show_help
        )
        set "PROXY=%~2"
        call :log "设置代理: !PROXY!"
        shift & shift
        goto :parse_args
    )
    if /i "!_arg!" == "--proxy" (
        if "%~2" == "" (
            call :log_error "--proxy 选项需要一个参数"
            goto :show_help
        )
        set "PROXY=%~2"
        call :log "设置代理: !PROXY!"
        shift & shift
        goto :parse_args
    )
    
    REM 处理开关选项
    if /i "!_arg!" == "-h" set "SHOW_HELP=1" & shift & goto :parse_args
    if /i "!_arg!" == "--help" set "SHOW_HELP=1" & shift & goto :parse_args
    if /i "!_arg!" == "-d" set "DEBUG=--debug" & call :log "启用调试模式" & shift & goto :parse_args
    if /i "!_arg!" == "--debug" set "DEBUG=--debug" & call :log "启用调试模式" & shift & goto :parse_args
    if /i "!_arg!" == "-f" set "FORCE=--force" & call :log "启用强制下载" & shift & goto :parse_args
    if /i "!_arg!" == "--force" set "FORCE=--force" & call :log "启用强制下载" & shift & goto :parse_args
    if /i "!_arg!" == "--no-verify" set "NO_VERIFY=--no-verify" & call :log "禁用SSL验证" & shift & goto :parse_args
    
    REM 未知选项
    call :log_warning "未知选项: !_arg!"
    shift
    goto :parse_args
)

REM 处理URL参数（非选项参数）
if not defined URL (
    REM 保存完整的URL，保留所有特殊字符
    set "_raw_url=%~1"
    call :log "原始URL: !_raw_url!"
    
    REM 移除外层引号
    set "_url=!_raw_url!"
    if "!_url:~0,1!"=="""" set "_url=!_url:~1,-1!"
    if "!_url:~0,1!"=="'" set "_url=!_url:~1,-1!"
    
    REM 转义URL中的特殊字符
    set "_url=!_url:?=^?!"
    set "_url=!_url:&=^&!"
    set "_url=!_url:|=^|!"
    set "_url=!_url:>=^>!"
    set "_url=!_url:<=^<!"
    set "_url=!_url:%%=^%%!"
    
    REM 设置最终URL
    set "URL=!_url!"
    call :log "处理后的URL: !URL!"
    shift
    goto :parse_args
)

shift
goto :parse_args

:check_args
if defined SHOW_HELP goto :show_help
if not defined URL (
    call :log_error "缺少必要参数: URL"
    goto :show_help
)

REM 记录最终参数
call :log "=== 参数解析完成 ==="
call :log "URL: !URL!"
call :log "输出目录: !OUTPUT_DIR!"
if defined PROXY call :log "代理服务器: !PROXY!"
if defined DEBUG call :log "调试模式: 已启用"
if defined FORCE call :log "强制下载: 已启用"
if defined NO_VERIFY call :log "SSL验证: 已禁用"

REM Setup virtual environment
call :log "正在设置虚拟环境..."
python scripts\venv_manager.py
if errorlevel 1 (
    call :log_error "虚拟环境设置失败"
    echo Error setting up virtual environment
    exit /b 1
)

REM Get virtual environment Python path
call :log "获取Python解释器路径..."
for /f "tokens=*" %%i in ('python -c "from scripts.venv_manager import get_venv_python; print(get_venv_python())"') do (
    if errorlevel 1 (
        call :log_error "获取Python路径失败"
        exit /b 1
    )
    set VENV_PYTHON=%%i
)
call :log "使用Python路径: !VENV_PYTHON!"

REM 构建Python命令参数
set "PY_ARGS=download"
call :log "构建Python命令参数..."

REM 使用单引号包裹整个URL参数，避免特殊字符问题
set ^"PY_ARGS=!PY_ARGS! "--url=!URL!"^"
set ^"PY_ARGS=!PY_ARGS! "--output=!OUTPUT_DIR!"^"
if defined PROXY set ^"PY_ARGS=!PY_ARGS! "--proxy=!PROXY!"^"
if defined DEBUG set "PY_ARGS=!PY_ARGS! !DEBUG!"
if defined FORCE set "PY_ARGS=!PY_ARGS! !FORCE!"
if defined NO_VERIFY set "PY_ARGS=!PY_ARGS! !NO_VERIFY!"

REM 执行Python命令
call :log "执行命令: !VENV_PYTHON! -m crx_toolkit.cli !PY_ARGS!"
"!VENV_PYTHON!" -m crx_toolkit.cli !PY_ARGS!

if errorlevel 1 (
    call :log_error "下载失败，错误码: !errorlevel!"
    call :log_error "失败URL: !URL!"
    echo Error occurred while downloading extension
    exit /b 1
)

REM 检查下载结果
if not exist "!OUTPUT_DIR!\*" (
    call :log_error "下载可能成功但输出目录为空: !OUTPUT_DIR!"
    echo Warning: Output directory is empty
    exit /b 1
)

call :log "扩展下载成功"
call :log "=== 下载任务结束 ==="
echo Successfully downloaded extension
exit /b 0

:show_help
echo.
echo Chrome扩展下载工具
echo.
echo 用法:
echo   %~n0 [选项] ^<url^>
echo.
echo 选项:
echo   -h, --help         显示帮助信息
echo   -o, --output       指定输出目录 (默认: output)
echo   -p, --proxy        设置代理服务器 (例如: http://127.0.0.1:7890)
echo   -d, --debug        启用调试模式
echo   -f, --force        强制重新下载
echo   --no-verify        禁用SSL验证
echo.
echo 示例:
echo   %~n0 "https://chromewebstore.google.com/detail/extension-name/extension-id"
echo   %~n0 -o "my_extensions" "https://chromewebstore.google.com/detail/extension-id"
echo   %~n0 -p "http://127.0.0.1:7890" "https://chromewebstore.google.com/detail/extension-id"
echo.
exit /b 1

:log
echo [%date% %time%] %* >> "%LOG_FILE%"
echo %*
goto :eof

:log_error
echo [%date% %time%] ERROR: %* >> "%LOG_FILE%"
echo ERROR: %*
goto :eof

:log_warning
echo [%date% %time%] WARNING: %* >> "%LOG_FILE%"
echo WARNING: %*
goto :eof