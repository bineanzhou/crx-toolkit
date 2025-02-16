#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
 fi

# 检查 PIL 库
python3 -c "from PIL import Image" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Error: Python Pillow library is required but not installed."
    echo "Please install it using: pip install Pillow"
    exit 1
fi

# 显示帮助信息
show_help() {
    echo "用法: crx_convert_icon <源图片> <扩展目录>"
    echo ""
    echo "将图片转换为 Chrome 扩展所需的各种尺寸的图标"
    echo ""
    echo "参数说明:"
    echo "  源图片         源图片文件路径"
    echo "  扩展目录       Chrome 扩展目录路径"
    echo ""
    echo "示例:"
    echo "  crx_convert_icon logo.png ~/my-extension                  # 使用相对路径"
    echo "  crx_convert_icon /path/to/icon.png /path/to/extension    # 使用绝对路径"
    echo "  crx_convert_icon ./assets/icon.jpg ./extension           # 支持 JPG 格式"
    echo "  crx_convert_icon ../resources/logo.png ./chrome-ext      # 使用上级目录的图片"
    exit 1
}

# 检查参数数量
if [ $# -ne 2 ]; then
    show_help
fi

# 添加项目根目录到 Python 路径
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# 运行 Python 脚本
PYTHONPATH="$ROOT_DIR/src" python3 -c "from crx_toolkit.crx_icon_converter import convert_crx_icon; convert_crx_icon()" "$1" "$2"