# CRX Toolkit CLI 使用文档

## 命令概览

CRX Toolkit 提供以下命令行工具：

- `pack`: 打包 Chrome 扩展为 CRX 文件
- `download`: 下载 CRX 文件
- `parse`: 解析 CRX 文件信息

## 详细命令说明

### pack - 打包扩展

将 Chrome 扩展目录打包为 CRX 文件。

```bash
python -m crx_toolkit.cli pack \
    --source <扩展目录> \
    --key <私钥文件> \
    --output <输出目录>
```

参数说明：
- `--source`: 扩展源目录路径
- `--key`: 私钥文件路径
- `--output`: 输出目录路径

### download - 下载扩展

从指定 URL 下载 CRX 文件。

```bash
python -m crx_toolkit.cli download \
    --url <下载链接> \
    --output <输出目录>
```

参数说明：
- `--url`: CRX 文件的下载链接
- `--output`: 保存文件的目录

### parse - 解析扩展

解析并显示 CRX 文件的信息。

```bash
python -m crx_toolkit.cli parse \
    --file <CRX文件>
```

参数说明：
- `--file`: 要解析的 CRX 文件路径

## 使用示例

### 打包扩展
```bash
# Windows
pack_crx.bat "C:\extensions\my_extension" "C:\keys\private.pem" "C:\output"

# Linux/macOS
./pack_crx.sh ~/extensions/my_extension ~/keys/private.pem ~/output
```

### 下载扩展
```bash
# Windows
download_crx.bat "https://example.com/extension.crx" "C:\output"

# Linux/macOS
./download_crx.sh https://example.com/extension.crx ~/output
```

### 解析扩展
```bash
# Windows
parse_crx.bat "C:\output\extension.crx"

# Linux/macOS
./parse_crx.sh ~/output/extension.crx
``` 