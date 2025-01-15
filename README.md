# CRX 工具库

## 简介
CRX 工具库是一个支持跨平台的 Python 库，用于创建、下载和解析 CRX 文件（Chrome 扩展包格式）。该工具提供统一接口，可以在 Windows、Linux 和 macOS 上轻松操作 CRX 文件，并支持通过外部封装的批处理脚本（bat 和 sh）方便使用。

---

## 功能

- **跨平台支持**：兼容 Windows、Linux 和 macOS。
- **CRX 文件打包**：从扩展源目录生成 CRX 文件，并通过私钥进行签名。
- **CRX 文件下载**：直接从网络下载 CRX 文件，并进行完整性校验。
- **CRX 文件解析**：提取和分析 CRX 文件内容。
- **命令行工具**：提供友好的 CLI 接口，快速完成操作。
- **外部脚本支持**：封装了 bat 和 sh 脚本，便于直接调用。
- **模块化设计**：灵活的架构，可集成到更大的项目中。

---

## 安装

1. 克隆项目代码：
   ```bash
   git clone https://github.com/yourusername/crx_toolkit.git
   cd crx_toolkit
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

---

## 使用说明

### 脚本使用

#### Windows（bat 脚本）

1. **打包 CRX 文件**
创建 `pack_crx.bat` 文件：
```bat
@echo off
python -m crx_toolkit.cli pack --source "%1" --key "%2" --output "%3"
```
使用：
```cmd
pack_crx.bat "扩展目录路径" "私钥文件路径" "输出目录"
```

2. **下载 CRX 文件**
创建 `download_crx.bat` 文件：
```bat
@echo off
python -m crx_toolkit.cli download --url "%1" --output "%2"
```
使用：
```cmd
download_crx.bat "下载链接" "输出目录"
```

#### Linux/macOS（sh 脚本）

1. **打包 CRX 文件**
创建 `pack_crx.sh` 文件：
```bash
#!/bin/bash
python -m crx_toolkit.cli pack --source "$1" --key "$2" --output "$3"
```
使用：
```bash
bash pack_crx.sh "扩展目录路径" "私钥文件路径" "输出目录"
```

2. **下载 CRX 文件**
创建 `download_crx.sh` 文件：
```bash
#!/bin/bash
python -m crx_toolkit.cli download --url "$1" --output "$2"
```
使用：
```bash
bash download_crx.sh "下载链接" "输出目录"
```

---

## 开源协议

本项目采用 MIT 开源协议，详情请参见 [LICENSE](LICENSE) 文件。

---

## 贡献

欢迎贡献！请提交 issue 或 pull request，帮助我们改进工具库。

---

## 联系方式

如有任何问题或建议，提交Issue：[Issue](https://github.com/bineanzhou/crx-toolkit/issues)

