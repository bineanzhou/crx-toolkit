# CRX Toolkit

一个跨平台的 Chrome 扩展打包工具，支持 Windows、Linux 和 macOS。

## 功能特点

- 支持跨平台（Windows、Linux、macOS）
- 自动检测和安装依赖（Node.js、npm、terser）
- JavaScript 代码混淆（使用 terser）
- 详细的日志记录
- 支持强制覆盖已存在的文件
- 文件过滤（自动排除 .git、.svn 等）
- 支持自定义私钥

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
crx-pack -s <源目录> -k <私钥文件> -o <输出目录>

# 使用混淆（需要 Node.js 和 npm）
crx-pack -s <源目录> -k <私钥文件> -o <输出目录> --use-terser

# 详细日志
crx-pack -s <源目录> -k <私钥文件> -o <输出目录> -v

# 跳过验证
crx-pack -s <源目录> -k <私钥文件> -o <输出目录> --no-verify
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
│       ├── packer.py       # 核心打包逻辑
│       └── utils/
│           └── file_utils.py
├── tests/                  # 测试文件
├── scripts/                # 批处理脚本
│   ├── pack_crx.bat       # Windows 批处理脚本
│   └── pack_crx.sh        # Linux/macOS 脚本
├── README.md
├── requirements.txt
└── setup.py
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

