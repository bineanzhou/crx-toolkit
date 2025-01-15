#!/bin/bash
# Parse CRX file and display information

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <crx_file>"
    exit 1
fi

python -m crx_toolkit.cli parse --file "$1"
if [ $? -ne 0 ]; then
    echo "Error occurred while parsing extension"
    exit 1
fi 