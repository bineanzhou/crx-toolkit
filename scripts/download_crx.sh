#!/bin/bash
# Download CRX file from URL

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <url> <output_dir>"
    exit 1
fi

# 使用 CRX Toolkit CLI 下载指定 URL 的 CRX 文件
# 通过传入的参数 $1（URL）和 $2（输出目录）调用下载命令
python -m crx_toolkit.cli download --url "$1" --output "$2"
if [ $? -ne 0 ]; then
    echo "Error occurred while downloading extension"
    exit 1
fi
echo "Successfully downloaded extension" 