#!/bin/bash
# Pack Chrome extension into CRX format

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <source_dir> <private_key> <output_dir>"
    exit 1
fi

python -m crx_toolkit.cli pack --source "$1" --key "$2" --output "$3"
if [ $? -ne 0 ]; then
    echo "Error occurred while packing extension"
    exit 1
fi
echo "Successfully packed extension" 