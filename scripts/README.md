# CRX Toolkit Scripts

This directory contains helper scripts for common CRX toolkit operations.

## Windows Scripts (.bat)

### Pack Extension
```batch
pack_crx.bat <source_dir> <private_key> <output_dir>
```

### Download Extension
```batch
download_crx.bat <url> <output_dir>
```

### Parse Extension
```batch
parse_crx.bat <crx_file>
```

## Linux/macOS Scripts (.sh)

First, make scripts executable:
```bash
chmod +x *.sh
```

### Pack Extension
```bash
./pack_crx.sh <source_dir> <private_key> <output_dir>
```

### Download Extension
```bash
./download_crx.sh <url> <output_dir>
```

### Parse Extension
```bash
./parse_crx.sh <crx_file>
```

## Examples

### Windows
```batch
pack_crx.bat "C:\extensions\my_extension" "C:\keys\private.pem" "C:\output"
download_crx.bat "https://example.com/extension.crx" "C:\output"
parse_crx.bat "C:\output\extension.crx"
```

### Linux/macOS
```bash
./pack_crx.sh ~/extensions/my_extension ~/keys/private.pem ~/output
./download_crx.sh https://example.com/extension.crx ~/output
./parse_crx.sh ~/output/extension.crx
``` 