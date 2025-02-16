# CRX Toolkit

一个跨平台的 Chrome 扩展打包工具，支持 Windows、Linux 和 macOS。

## 功能特点

- 支持跨平台（Windows、Linux、macOS）
- 支持 CRX 文件的打包、下载和解析
- 支持从 Chrome Web Store 直接下载扩展
- 支持多种打包格式（CRX、ZIP）
- 支持自定义私钥签名和签名验证
- 支持 JavaScript 代码混淆（通过 terser）
- 提供详细的日志记录和错误处理
- 提供命令行工具和 Python API
- 支持代理设置（下载时）
- 支持强制覆盖已存在文件

## 安装要求

- Python 3.6+
- OpenSSL（用于生成和处理私钥）
- Node.js 和 npm（可选，仅在需要 JavaScript 混淆时需要）

## 安装方法

```bash
# 通过 pip 安装
pip install crx-toolkit

# 或从源码安装
git clone https://github.com/yourusername/crx-toolkit.git
cd crx-toolkit
pip install -e .
```

## 使用方法

### 命令行工具

1. 打包扩展：

```bash
# 基本用法（自动生成私钥）
pack_crx.sh <扩展目录>

# 指定私钥和输出目录
pack_crx.sh <扩展目录> -k <私钥文件> -o <输出目录>

# 打包为 ZIP 格式
pack_crx.sh <扩展目录> --format zip

# 启用 JavaScript 混淆
pack_crx.sh <扩展目录> --use-terser

# 更多选项
pack_crx.sh --help
```

2. 下载扩展：

```bash
# 从 Chrome Web Store 下载
download_crx.sh <扩展ID或URL>

# 使用代理
download_crx.sh -p "http://127.0.0.1:7890" <扩展URL>

# 指定输出目录
download_crx.sh -o <输出目录> <扩展URL>
```

3. 解析 CRX：

```bash
# 解析 CRX 文件信息
parse_crx.sh <CRX文件路径>
```

### Python API

```python
from crx_toolkit import pack_extension, download_extension, parse_crx

# 打包扩展
pack_extension(
    source_dir="path/to/extension",
    private_key_path="path/to/key.pem",  # 可选，不提供时自动生成
    output_dir="path/to/output",
    force=True,              # 覆盖已存在的文件
    verbose=False,           # 详细日志
    no_verify=False,         # 跳过签名验证
    use_terser=False,        # 使用 terser 混淆
    use_zip=False           # 使用 ZIP 格式
)

# 下载扩展
download_extension(
    url="https://chrome.google.com/webstore/detail/extension-id",
    output_dir="path/to/output",
    proxy="http://127.0.0.1:7890"  # 可选
)

# 解析 CRX
parse_crx("path/to/extension.crx")
```

## 项目结构

```
crx-toolkit/
├── src/
│   └── crx_toolkit/
│       ├── __init__.py
│       ├── cli.py         # 命令行接口
│       ├── packer.py      # 打包功能
│       ├── downloader.py  # 下载功能
│       ├── parser.py      # CRX解析
│       ├── signer.py      # 签名功能
│       └── utils/         # 工具函数
├── docs/                  # 文档目录
│   ├── CONTRIBUTING.md    # 贡献指南
│   ├── api.md            # API文档
│   ├── cli.md            # CLI使用文档
│   └── development.md     # 开发文档
├── scripts/               # 脚本目录
│   ├── download_crx.bat   # Windows下载脚本
│   ├── download_crx.sh    # Unix下载脚本
│   ├── pack_crx.bat      # Windows打包脚本
│   └── pack_crx.sh       # Unix打包脚本
└── README.md             # 项目说明
```

