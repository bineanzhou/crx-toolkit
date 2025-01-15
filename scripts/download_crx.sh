#!/bin/bash
# Download CRX file from URL

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <url> <output_dir>"
    echo "Examples:"
    echo "  $0 'https://chromewebstore.google.com/detail/extension-name/extension-id' 'output'"
    echo "  $0 'https://example.com/extension.crx' 'output'"
    echo "Note: Always wrap the URL in quotes"
    exit 1
fi

# Setup virtual environment
python3 scripts/venv_manager.py
if [ $? -ne 0 ]; then
    echo "Error setting up virtual environment"
    exit 1
fi

# Get virtual environment Python path
VENV_PYTHON=$(python3 -c "from scripts.venv_manager import get_venv_python; print(get_venv_python())")

# Call Python script with the URL
"$VENV_PYTHON" -m crx_toolkit.cli download --url="$1" --output="$2"
if [ $? -ne 0 ]; then
    echo "Error occurred while downloading extension"
    exit 1
fi

echo "Successfully downloaded extension"
exit 0 