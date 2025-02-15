# CRX Toolkit

一个跨平台的 Chrome 扩展打包工具，支持 Windows、Linux 和 macOS。

## 功能特点

- 支持跨平台（Windows、Linux、macOS）
- 支持 CRX 文件的打包、下载和解析
- 支持从 Chrome Web Store 直接下载扩展
- 详细的日志记录和错误处理
- 支持强制覆盖已存在的文件
- 支持多种打包格式（CRX、ZIP）
- 支持自定义私钥签名
- 提供完整的命令行工具和 Python API

## 安装要求

- Python 3.6+
- Node.js（可选，用于 JavaScript 混淆）
- npm（可选，用于安装 terser）

## 安装方法

```bash
pip install crx-toolkit
```

## 使用方法

### 命令行工具

1. 打包扩展：

```bash
# 基本用法
python -m crx_toolkit.cli pack -s <源目录> -k <私钥文件> -o <输出目录>

# 指定打包格式（crx 或 zip）
python -m crx_toolkit.cli pack -s <源目录> -k <私钥文件> -o <输出目录> --format crx

# 强制覆盖已存在文件
python -m crx_toolkit.cli pack -s <源目录> -k <私钥文件> -o <输出目录> -f

# 启用详细日志
python -m crx_toolkit.cli pack -s <源目录> -k <私钥文件> -o <输出目录> -v
```

2. 下载扩展：

```bash
# 从 Chrome Web Store 下载
python -m crx_toolkit.cli download <扩展ID或URL> -o <输出目录>
```

3. 解析 CRX：

```bash
# 解析 CRX 文件信息
python -m crx_toolkit.cli parse <CRX文件路径>
```

### Python API

```python
from crx_toolkit import pack_extension

# 基本用法
pack_extension(
    source_dir="path/to/extension",
    private_key_path="path/to/key.pem",
    output_dir="path/to/output",
    force=True,              # 覆盖已存在的文件
    verbose=False,           # 详细日志
    no_verify=False,         # 跳过验证
    use_terser=False        # 使用 terser 混淆
)
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
│   ├── pack_crx.sh       # Unix打包脚本
│   ├── parse_crx.bat     # Windows解析脚本
│   └── parse_crx.sh      # Unix解析脚本
├── README.md             # 项目说明
├── requirements.txt      # 依赖清单
└── setup.py             # 安装配置
```

## 开发文档

### 核心模块

#### packer.py

主要功能模块，包含以下关键函数：

- `pack_extension()`: 打包扩展的主函数
- `minify_js_file()`: JavaScript 文件混淆
- `check_nodejs_installed()`: 检查 Node.js 环境
- `install_terser()`: 安装 terser
- `ensure_terser_available()`: 确保 terser 可用
- `setup_logging()`: 配置日志系统

### 环境检测和依赖管理

1. Node.js 检测
   - 自动检测常见安装路径
   - 支持 Windows 和 Unix 路径
   - PATH 环境变量检查

2. Terser 管理
   - 自动检测安装状态
   - 支持本地和全局安装
   - 自动安装功能

### 日志系统

- 支持文件和控制台输出
- 可配置详细程度（DEBUG/INFO）
- 自动清理历史日志

### 错误处理

- 完整的异常捕获和处理
- 详细的错误信息记录
- 用户友好的错误提示

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始发布
- 基本打包功能
- JavaScript 混淆支持
- 跨平台支持

