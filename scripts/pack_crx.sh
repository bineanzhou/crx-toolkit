#!/bin/bash
# Pack Chrome extension into CRX format
set -e

# 设置日志文件
LOG_FILE="crx_pack.log"

# 获取脚本所在目录的上级目录(项目根目录)
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 初始化参数默认值
SOURCE_DIR=""
KEY_FILE=""
OUTPUT_DIR="output"
DEBUG=""
FORCE=""
NO_VERIFY=""
USE_TERSER=""
FORMAT="crx"

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

show_help() {
    echo
    echo "Chrome扩展打包工具"
    echo
    echo "用法:"
    echo "  $(basename "$0") <扩展目录> [选项]"
    echo
    echo "参数:"
    echo "  扩展目录        Chrome扩展的源目录路径"
    echo
    echo "选项:"
    echo "  -h, --help         显示帮助信息"
    echo "  -o, --output       指定输出目录 (默认: output)"
    echo "  -k, --key          指定私钥文件路径（仅在打包为crx格式时需要）"
    echo "  --format          打包格式: crx 或 zip (默认: crx)"
    echo "  -d, --debug        启用详细输出模式 (--verbose)"
    echo "  -f, --force        强制重新打包"
    echo "  --no-verify        禁用签名验证"
    echo "  --use-terser      启用JavaScript代码混淆"
    echo
    echo "示例:"
    echo "  $(basename "$0") \"扩展目录\""
    echo "  $(basename "$0") \"扩展目录\" -k \"private.pem\""
    echo "  $(basename "$0") \"扩展目录\" -o \"my_crx\" -k \"private.pem\""
    echo "  $(basename "$0") \"扩展目录\" --format zip"
    echo "  $(basename "$0") \"扩展目录\" -d --use-terser -k \"private.pem\""
    echo
    exit 1
}

# 记录开始执行
log "=== 开始解析参数 ==="
log "原始参数列表: $*"
log "项目根目录: $ROOT_DIR"

# 检查是否有帮助选项
for arg in "$@"; do
    if [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
        show_help
    fi
done

# 检查第一个参数是否为扩展目录
if [ $# -eq 0 ]; then
    log_error "缺少必要参数: 扩展目录"
    show_help
fi

# 设置源目录
SOURCE_DIR="$1"
log "设置源目录: $SOURCE_DIR"
shift

# 解析命令行选项
while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help)
            show_help
            ;;
        -o|--output)
            if [ -z "$2" ]; then
                log_error "${1} 选项需要一个参数"
                show_help
            fi
            OUTPUT_DIR="$2"
            log "设置输出目录: $OUTPUT_DIR"
            shift 2
            ;;
        -k|--key)
            if [ -z "$2" ]; then
                log_error "${1} 选项需要一个参数"
                show_help
            fi
            KEY_FILE="$2"
            log "设置私钥文件: $KEY_FILE"
            shift 2
            ;;
        --format)
            if [ -z "$2" ]; then
                log_error "--format 选项需要一个参数"
                show_help
            fi
            FORMAT="$2"
            if [ "$FORMAT" != "crx" ] && [ "$FORMAT" != "zip" ]; then
                log_error "无效的格式: $FORMAT，必须是 'crx' 或 'zip'"
                show_help
            fi
            log "设置打包格式: $FORMAT"
            shift 2
            ;;
        -d|--debug)
            DEBUG="--verbose"
            log "启用详细输出模式"
            shift
            ;;
        -f|--force)
            FORCE="--force"
            log "启用强制打包"
            shift
            ;;
        --no-verify)
            NO_VERIFY="--no-verify"
            log "禁用签名验证"
            shift
            ;;
        --use-terser)
            USE_TERSER="--use-terser"
            log "启用JS代码混淆"
            shift
            ;;
        -*)
            log_warning "未知选项: $1"
            shift
            ;;
        *)
            log_warning "跳过多余参数: $1"
            shift
            ;;
    esac
done

# 检查必要参数
if [ -z "$SOURCE_DIR" ]; then
    log_error "缺少必要参数: 源目录"
    show_help
fi

# 获取当前工作目录
CURR_DIR="$(pwd)"
log "当前工作目录: $CURR_DIR"

# 如果是crx格式且没有提供私钥，自动创建私钥文件
if [ "$FORMAT" = "crx" ] && [ -z "$KEY_FILE" ]; then
    KEY_FILE="$CURR_DIR/key.pem"
    log "未提供私钥文件，将使用默认私钥文件: $KEY_FILE"
    
    # 如果私钥文件不存在，则创建新的私钥文件
    if [ ! -f "$KEY_FILE" ]; then
        log "私钥文件不存在，将创建新的私钥文件"
        
        # 使用 openssl 生成私钥
        openssl genpkey -algorithm RSA -out "$KEY_FILE" -pkeyopt rsa_keygen_bits:2048 || {
            log_error "生成私钥文件失败"
            exit 1
        }
        
        log "成功生成私钥文件: $KEY_FILE"
    else
        log "使用已存在的私钥文件: $KEY_FILE"
    fi
fi

# 记录最终参数
log "=== 参数解析完成 ==="
log "源目录: $SOURCE_DIR"
[ -n "$KEY_FILE" ] && log "私钥文件: $KEY_FILE"
log "输出目录: $OUTPUT_DIR"
log "打包格式: $FORMAT"

# 设置虚拟环境
log "正在设置虚拟环境..."
python "$ROOT_DIR/scripts/venv_manager.py"
if [ $? -ne 0 ]; then
    log_error "虚拟环境设置失败"
    echo "Error setting up virtual environment"
    exit 1
fi

# 获取虚拟环境Python路径
log "获取Python解释器路径..."
VENV_PYTHON=$(python -c "import os,sys; sys.path.insert(0, r'$ROOT_DIR/scripts'); from venv_manager import get_venv_python; print(get_venv_python())")
if [ $? -ne 0 ] || [ -z "$VENV_PYTHON" ]; then
    log_error "未能获取到Python解释器路径"
    exit 1
fi

log "使用Python路径: $VENV_PYTHON"

# 构建Python命令参数
PY_ARGS="pack"
log "构建Python命令参数..."

# 转换为绝对路径
CURR_DIR="$(pwd)"

# 处理源目录路径
if [ "${SOURCE_DIR:0:1}" = "/" ]; then
    ABS_SOURCE_DIR="$SOURCE_DIR"
else
    ABS_SOURCE_DIR="$CURR_DIR/$SOURCE_DIR"
fi

if [ ! -d "$ABS_SOURCE_DIR" ]; then
    log_error "源目录不存在: $SOURCE_DIR"
    exit 1
fi
SOURCE_DIR="$ABS_SOURCE_DIR"

# 处理私钥文件路径（如果提供）
if [ -n "$KEY_FILE" ]; then
    if [ "${KEY_FILE:0:1}" = "/" ]; then
        ABS_KEY_FILE="$KEY_FILE"
    else
        ABS_KEY_FILE="$CURR_DIR/$KEY_FILE"
    fi

    if [ ! -f "$ABS_KEY_FILE" ]; then
        log_error "私钥文件不存在: $KEY_FILE"
        exit 1
    fi
    KEY_FILE="$ABS_KEY_FILE"
fi

# 处理输出目录路径
if [ "${OUTPUT_DIR:0:1}" = "/" ]; then
    ABS_OUTPUT_DIR="$OUTPUT_DIR"
else
    ABS_OUTPUT_DIR="$CURR_DIR/$OUTPUT_DIR"
fi

mkdir -p "$ABS_OUTPUT_DIR" || {
    log_error "无法创建输出目录: $OUTPUT_DIR"
    exit 1
}
OUTPUT_DIR="$ABS_OUTPUT_DIR"

# 记录路径信息
log "路径信息:"
log "  当前目录: $CURR_DIR"
log "  源目录: $SOURCE_DIR"
[ -n "$KEY_FILE" ] && log "  私钥文件: $KEY_FILE"
log "  输出目录: $OUTPUT_DIR"

# 添加必要参数
PY_ARGS="$PY_ARGS --source \"$SOURCE_DIR\" --output \"$OUTPUT_DIR\""

# 添加私钥参数（如果提供）
[ -n "$KEY_FILE" ] && PY_ARGS="$PY_ARGS --key \"$KEY_FILE\""

# 添加格式参数
PY_ARGS="$PY_ARGS --format $FORMAT"

# 添加可选参数
[ -n "$DEBUG" ] && PY_ARGS="$PY_ARGS --verbose" && log "启用详细输出模式"
[ -n "$FORCE" ] && PY_ARGS="$PY_ARGS --force" && log "启用强制模式"
[ -n "$NO_VERIFY" ] && PY_ARGS="$PY_ARGS --no-verify" && log "禁用验证"
[ -n "$USE_TERSER" ] && PY_ARGS="$PY_ARGS --use-terser" && log "启用JS代码混淆"

# 执行Python命令
log "执行命令: \"$VENV_PYTHON\" -m crx_toolkit.cli $PY_ARGS"
eval "\"$VENV_PYTHON\" -m crx_toolkit.cli $PY_ARGS"

if [ $? -ne 0 ]; then
    log_error "打包失败，错误码: $?"
    echo "Error occurred while packing extension"
    exit 1
fi

# 检查输出结果
if ! ls "$OUTPUT_DIR"/* >/dev/null 2>&1; then
    log_error "打包可能成功但输出目录为空: $OUTPUT_DIR"
    echo "Warning: Output directory is empty"
    exit 1
fi

log "扩展打包成功"
log "=== 打包任务结束 ==="
echo "Successfully packed extension"
exit 0