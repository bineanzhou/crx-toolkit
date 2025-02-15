@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

REM 设置日志文件
set "LOG_FILE=crx_pack.log"

REM 获取脚本所在目录的上级目录(项目根目录)
pushd "%~dp0.."
set "ROOT_DIR=%CD%"
popd

REM 初始化参数默认值
set "SOURCE_DIR="
set "KEY_FILE="
set "OUTPUT_DIR=output"
set "DEBUG="
set "FORCE="
set "NO_VERIFY="
set "USE_TERSER="
set "FORMAT=crx"

REM 记录开始执行
call :log "=== 开始解析参数 ==="
call :log "原始参数列表: %*"
call :log "项目根目录: !ROOT_DIR!"

REM 解析命令行参数
:parse_args
if "%~1"=="" goto :check_args

REM 记录当前处理的参数
call :log "处理参数: [%~1]"

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
    if /i "!_arg!" == "--format" (
        if "%~2" == "" (
            call :log_error "--format 选项需要一个参数"
            goto :show_help
        )
        set "FORMAT=%~2"
        if not "!FORMAT!" == "crx" if not "!FORMAT!" == "zip" (
            call :log_error "无效的格式: !FORMAT!，必须是 'crx' 或 'zip'"
            goto :show_help
        )
        call :log "设置打包格式: !FORMAT!"
        shift & shift
        goto :parse_args
    )
    
    REM 处理开关选项
    if /i "!_arg!" == "-h" set "SHOW_HELP=1" & shift & goto :parse_args
    if /i "!_arg!" == "--help" set "SHOW_HELP=1" & shift & goto :parse_args
    if /i "!_arg!" == "-d" set "DEBUG=--verbose" & call :log "启用详细输出模式" & shift & goto :parse_args
    if /i "!_arg!" == "--debug" set "DEBUG=--verbose" & call :log "启用详细输出模式" & shift & goto :parse_args
    if /i "!_arg!" == "-f" set "FORCE=--force" & call :log "启用强制打包" & shift & goto :parse_args
    if /i "!_arg!" == "--force" set "FORCE=--force" & call :log "启用强制打包" & shift & goto :parse_args
    if /i "!_arg!" == "--no-verify" set "NO_VERIFY=--no-verify" & call :log "禁用签名验证" & shift & goto :parse_args
    if /i "!_arg!" == "--use-terser" set "USE_TERSER=--use-terser" & call :log "启用JS代码混淆" & shift & goto :parse_args
    
    REM 未知选项
    call :log_warning "未知选项: !_arg!"
    shift
    goto :parse_args
)

REM 检查第一个参数是否为扩展目录
if not defined SOURCE_DIR (
    if "%~1" == "" (
        call :log_error "缺少必要参数: 扩展目录"
        goto :show_help
    )
    set "SOURCE_DIR=%~1"
    call :log "设置源目录: !SOURCE_DIR!"
    shift
    goto :parse_args
)

REM 跳过多余的参数
call :log_warning "跳过多余参数: %~1"
shift
goto :parse_args

:check_args
if defined SHOW_HELP goto :show_help

REM 检查必要参数
if not defined SOURCE_DIR (
    call :log_error "缺少必要参数: 源目录"
    goto :show_help
)

REM 如果是crx格式且没有提供私钥，自动创建私钥文件
if "%FORMAT%"=="crx" if "%KEY_FILE%"=="" (
    set "KEY_FILE=%CD%\key.pem"
    call :log "未提供私钥文件，将使用默认私钥文件: %KEY_FILE%"
    
    REM 如果私钥文件不存在，则创建新的私钥文件
    if not exist "%KEY_FILE%" (
        call :log "私钥文件不存在，将创建新的私钥文件"
        
        REM 使用 openssl 生成私钥
        openssl genpkey -algorithm RSA -out "%KEY_FILE%" -pkeyopt rsa_keygen_bits:2048
        if errorlevel 1 (
            call :log_error "生成私钥文件失败"
            exit /b 1
        )
        
        call :log "成功生成私钥文件: %KEY_FILE%"
    ) else (
        call :log "使用已存在的私钥文件: %KEY_FILE%"
    )
)

REM 记录最终参数
call :log "=== 参数解析完成 ==="
call :log "源目录: !SOURCE_DIR!"
if defined KEY_FILE call :log "私钥文件: !KEY_FILE!"
call :log "输出目录: !OUTPUT_DIR!"
call :log "打包格式: !FORMAT!"

REM 设置虚拟环境
call :log "正在设置虚拟环境..."
python "!ROOT_DIR!\scripts\venv_manager.py"
if errorlevel 1 (
    call :log_error "虚拟环境设置失败"
    echo Error setting up virtual environment
    exit /b 1
)

REM 获取虚拟环境Python路径
call :log "获取Python解释器路径..."
set "PYTHON_CMD=import os,sys; sys.path.insert(0, r'%ROOT_DIR%/scripts'); from venv_manager import get_venv_python; print(get_venv_python())"
for /f "tokens=*" %%i in ('python -c "%PYTHON_CMD%"') do (
    if errorlevel 1 (
        call :log_error "获取Python路径失败"
        exit /b 1
    )
    set "VENV_PYTHON=%%i"
)

if not defined VENV_PYTHON (
    call :log_error "未能获取到Python解释器路径"
    exit /b 1
)

call :log "使用Python路径: !VENV_PYTHON!"

REM 构建Python命令参数
set "PY_ARGS=pack"
call :log "构建Python命令参数..."

REM 转换为绝对路径
set "CURR_DIR=%CD%"

REM 处理源目录路径
if "!SOURCE_DIR:~1,1!" == ":" (
    REM 已经是绝对路径
    set "ABS_SOURCE_DIR=!SOURCE_DIR!"
) else (
    REM 相对路径转绝对路径
    set "ABS_SOURCE_DIR=!CURR_DIR!\!SOURCE_DIR!"
)

pushd "!ABS_SOURCE_DIR!" 2>nul && (
    set "SOURCE_DIR=!CD!"
    popd
) || (
    call :log_error "源目录不存在: !SOURCE_DIR!"
    exit /b 1
)

REM 处理私钥文件路径（如果提供）
if defined KEY_FILE (
    if "!KEY_FILE:~1,1!" == ":" (
        REM 已经是绝对路径
        set "ABS_KEY_FILE=!KEY_FILE!"
    ) else (
        REM 相对路径转绝对路径
        set "ABS_KEY_FILE=!CURR_DIR!\!KEY_FILE!"
    )

    if exist "!ABS_KEY_FILE!" (
        set "KEY_FILE=!ABS_KEY_FILE!"
    ) else (
        call :log_error "私钥文件不存在: !KEY_FILE!"
        exit /b 1
    )
)

REM 处理输出目录路径
if "!OUTPUT_DIR:~1,1!" == ":" (
    REM 已经是绝对路径
    set "ABS_OUTPUT_DIR=!OUTPUT_DIR!"
) else (
    REM 相对路径转绝对路径
    set "ABS_OUTPUT_DIR=!CURR_DIR!\!OUTPUT_DIR!"
)

if not exist "!ABS_OUTPUT_DIR!" mkdir "!ABS_OUTPUT_DIR!"
pushd "!ABS_OUTPUT_DIR!" 2>nul && (
    set "OUTPUT_DIR=!CD!"
    popd
) || (
    call :log_error "无法创建输出目录: !OUTPUT_DIR!"
    exit /b 1
)

REM 记录路径信息
call :log "路径信息:"
call :log "  当前目录: !CURR_DIR!"
call :log "  源目录: !SOURCE_DIR!"
if defined KEY_FILE call :log "  私钥文件: !KEY_FILE!"
call :log "  输出目录: !OUTPUT_DIR!"

REM 添加必要参数，使用双引号包裹路径
set "PY_ARGS=!PY_ARGS! --source "!SOURCE_DIR!" --output "!OUTPUT_DIR!""

REM 添加私钥参数（如果提供）
if defined KEY_FILE set "PY_ARGS=!PY_ARGS! --key "!KEY_FILE!""

REM 添加格式参数
set "PY_ARGS=!PY_ARGS! --format !FORMAT!"

REM 添加可选参数
if defined DEBUG (
    set "PY_ARGS=!PY_ARGS! --verbose"
    call :log "启用详细输出模式"
)
if defined FORCE (
    set "PY_ARGS=!PY_ARGS! --force"
    call :log "启用强制模式"
)
if defined NO_VERIFY (
    set "PY_ARGS=!PY_ARGS! --no-verify"
    call :log "禁用验证"
)
if defined USE_TERSER (
    set "PY_ARGS=!PY_ARGS! --use-terser"
    call :log "启用JS代码混淆"
)

REM 执行Python命令
call :log "执行命令: "!VENV_PYTHON!" -m crx_toolkit.cli !PY_ARGS!"
"!VENV_PYTHON!" -m crx_toolkit.cli !PY_ARGS!

if errorlevel 1 (
    call :log_error "打包失败，错误码: !errorlevel!"
    echo Error occurred while packing extension
    exit /b 1
)

REM 检查输出结果
if not exist "!OUTPUT_DIR!\*" (
    call :log_error "打包可能成功但输出目录为空: !OUTPUT_DIR!"
    echo Warning: Output directory is empty
    exit /b 1
)

call :log "扩展打包成功"
call :log "=== 打包任务结束 ==="
echo Successfully packed extension
exit /b 0

REM 日志函数
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

:show_help
echo.
echo Chrome扩展打包工具
echo.
echo 用法:
echo   %~n0 ^<扩展目录^> [选项]
echo.
echo 参数:
echo   扩展目录        Chrome扩展的源目录路径
echo.
echo 选项:
echo   -h, --help         显示帮助信息
echo   -o, --output       指定输出目录 (默认: output)
echo   -k, --key          指定私钥文件路径（仅在打包为crx格式时需要）
echo   --format          打包格式: crx 或 zip (默认: crx)
echo   -d, --debug        启用详细输出模式 (--verbose)
echo   -f, --force        强制重新打包
echo   --no-verify        禁用签名验证
echo   --use-terser      启用JavaScript代码混淆
echo.
echo 示例:
echo   %~n0 "扩展目录"
echo   %~n0 "扩展目录" -k "private.pem"
echo   %~n0 "扩展目录" -o "my_crx" -k "private.pem"
echo   %~n0 "扩展目录" --format zip
echo   %~n0 "扩展目录" -d --use-terser -k "private.pem"
echo.
exit /b 1