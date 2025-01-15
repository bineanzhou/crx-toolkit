#!/bin/bash

# 设置日志文件
LOG_FILE="crx_download.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $*" | tee -a "$LOG_FILE"
}

# 显示帮助信息
show_help() {
    echo
    echo "Chrome扩展下载工具"
    echo
    echo "用法:"
    echo "  $(basename $0) [选项] <url>"
    echo
    echo "选项:"
    echo "  -h, --help         显示帮助信息"
    echo "  -o, --output       指定输出目录 (默认: output)"
    echo "  -p, --proxy        设置代理服务器 (例如: http://127.0.0.1:7890)"
    echo "  -d, --debug        启用调试模式"
    echo "  -f, --force        强制重新下载"
    echo "  --no-verify        禁用SSL验证"
    echo
    echo "示例:"
    echo "  $0 \"https://chromewebstore.google.com/detail/extension-name/extension-id\""
    echo "  $0 -o \"my_extensions\" \"https://chromewebstore.google.com/detail/extension-id\""
    echo "  $0 -p \"http://127.0.0.1:7890\" \"https://chromewebstore.google.com/detail/extension-id\""
    echo
    exit 1
}

# 初始化参数默认值
URL=""
OUTPUT_DIR="output"
PROXY=""
DEBUG=""
FORCE=""
NO_VERIFY=""

# 记录开始执行
log "=== 开始解析参数 ==="
log "原始参数列表: $*"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        -o|--output)
            if [ -z "$2" ]; then
                log_error "$1 选项需要一个参数"
                show_help
            fi
            OUTPUT_DIR="$2"
            log "设置输出目录: $OUTPUT_DIR"
            shift 2
            ;;
        -p|--proxy)
            if [ -z "$2" ]; then
                log_error "$1 选项需要一个参数"
                show_help
            fi
            PROXY="$2"
            log "设置代理: $PROXY"
            shift 2
            ;;
        -d|--debug)
            DEBUG="--debug"
            log "启用调试模式"
            shift
            ;;
        -f|--force)
            FORCE="--force"
            log "启用强制下载"
            shift
            ;;
        --no-verify)
            NO_VERIFY="--no-verify"
            log "禁用SSL验证"
            shift
            ;;
        *)
            if [ -z "$URL" ]; then
                URL="$1"
                log "设置下载URL: $URL"
            else
                log_warning "跳过多余参数: $1"
            fi
            shift
            ;;
    esac
done

# 检查必要参数
if [ -z "$URL" ]; then
    log_error "缺少必要参数: URL"
    show_help
fi

# 记录最终参数
log "=== 参数解析完成 ==="
log "URL: $URL"
log "输出目录: $OUTPUT_DIR"
[ -n "$PROXY" ] && log "代理服务器: $PROXY"
[ -n "$DEBUG" ] && log "调试模式: 已启用"
[ -n "$FORCE" ] && log "强制下载: 已启用"
[ -n "$NO_VERIFY" ] && log "SSL验证: 已禁用"

# 设置虚拟环境
log "正在设置虚拟环境..."
python3 scripts/venv_manager.py
if [ $? -ne 0 ]; then
    log_error "虚拟环境设置失败"
    echo "Error setting up virtual environment"
    exit 1
fi

# 获取虚拟环境Python路径
log "获取Python解释器路径..."
VENV_PYTHON=$(python3 -c "from scripts.venv_manager import get_venv_python; print(get_venv_python())")
if [ $? -ne 0 ]; then
    log_error "获取Python路径失败"
    exit 1
fi
log "使用Python路径: $VENV_PYTHON"

# 构建Python命令参数
PY_ARGS="download"
log "构建Python命令参数..."

# 添加必要参数
PY_ARGS="$PY_ARGS --url=\"$URL\" --output=\"$OUTPUT_DIR\""
[ -n "$PROXY" ] && PY_ARGS="$PY_ARGS --proxy=\"$PROXY\""
[ -n "$DEBUG" ] && PY_ARGS="$PY_ARGS $DEBUG"
[ -n "$FORCE" ] && PY_ARGS="$PY_ARGS $FORCE"
[ -n "$NO_VERIFY" ] && PY_ARGS="$PY_ARGS $NO_VERIFY"

# 执行Python命令
log "执行命令: $VENV_PYTHON -m crx_toolkit.cli $PY_ARGS"
eval "\"$VENV_PYTHON\" -m crx_toolkit.cli $PY_ARGS"

if [ $? -ne 0 ]; then
    log_error "下载失败，错误码: $?"
    log_error "失败URL: $URL"
    echo "Error occurred while downloading extension"
    exit 1
fi

# 检查下载结果
if [ ! "$(ls -A \"$OUTPUT_DIR\")" ]; then
    log_error "下载可能成功但输出目录为空: $OUTPUT_DIR"
    echo "Warning: Output directory is empty"
    exit 1
fi

log "扩展下载成功"
log "=== 下载任务结束 ==="
echo "Successfully downloaded extension"
exit 0 