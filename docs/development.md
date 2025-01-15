# CRX Toolkit 开发文档

## 项目结构

```plaintext
crx_toolkit/
├── src/
│   ├── crx_toolkit/
│   │   ├── __init__.py              # 初始化模块
│   │   ├── packer.py                # CRX 打包逻辑
│   │   ├── downloader.py            # CRX 下载模块
│   │   ├── parser.py                # CRX 解析模块
│   │   ├── signer.py                # CRX 签名逻辑
│   │   ├── cli.py                   # 命令行接口
│   │   └── utils/                   # 工具函数
│   └── tests/                       # 测试目录
├── scripts/                         # 脚本文件
├── docs/                           # 文档目录
└── examples/                       # 示例代码
```

## 核心模块说明

### 1. packer.py - 打包模块

主要负责将 Chrome 扩展目录打包为 CRX 格式。

```python
def pack_extension(source_dir: str, private_key_path: str, output_dir: str) -> str:
    """
    将扩展目录打包为 CRX 文件
    
    Args:
        source_dir: 扩展源目录路径
        private_key_path: 私钥文件路径
        output_dir: 输出目录路径
        
    Returns:
        str: 生成的 CRX 文件路径
    """
```

### 2. downloader.py - 下载模块

负责从 Chrome Web Store 和其他来源下载 CRX 文件。

#### 主要功能

1. **扩展 ID 提取**
```python
def extract_extension_id(url: str) -> Optional[str]:
    """
    从 Chrome Web Store URL 中提取扩展 ID
    支持的 URL 格式:
    - 新版: https://chromewebstore.google.com/detail/name/extension_id
    - 旧版: https://chrome.google.com/webstore/detail/extension_id
    - ID 格式: 32位小写字母
    """
```

2. **扩展下载**
```python
def download_crx(
    url: str,
    output_dir: str,
    filename: Optional[str] = None,
    proxy: Optional[str] = None,
    verify: bool = True,
    timeout: int = 30
) -> str:
    """
    从 Chrome Web Store 或其他来源下载扩展
    
    特性:
    - 支持多种下载 URL 格式
    - 自动重试不同的下载 API
    - 代理支持
    - SSL 验证选项
    - 超时控制
    """
```

3. **CRX 解压**
```python
def extract_crx(
    crx_path: str,
    extract_dir: Optional[str] = None
) -> str:
    """
    将下载的 CRX 文件解压到指定目录
    """
```

#### 下载 URL 格式

模块支持以下下载 URL 格式：

1. Chrome Web Store API (推荐):
```
https://clients2.google.com/service/update2/crx?response=redirect&acceptformat=crx2,crx3&prodversion=89.0.4389.90&x=id%3D{ID}%26installsource%3Dondemand%26uc
```

2. 备用 API:
```
https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&x=id%3D{ID}%26installsource%3Dondemand%26uc
```

3. 简化格式:
```
https://clients2.google.com/service/update2/crx?response=redirect&x=id%3D{ID}%26uc
```

#### 使用示例

1. 从 Chrome Web Store 下载:
```python
from crx_toolkit.downloader import download_crx, extract_crx

# 下载扩展
crx_path = download_crx(
    url="https://chromewebstore.google.com/detail/extension-name/extension-id",
    output_dir="./extensions/",
    proxy="http://127.0.0.1:7890"  # 可选代理
)

# 解压扩展
extract_dir = extract_crx(crx_path)
```

2. 使用直接下载链接:
```python
crx_path = download_crx(
    url="https://example.com/extension.crx",
    output_dir="./extensions/",
    filename="custom_name.crx"  # 自定义文件名
)
```

#### 错误处理

模块会抛出以下异常：

1. `ValueError`:
   - URL 无效
   - 无法提取扩展 ID

2. `RuntimeError`:
   - 下载失败
   - 文件太小或无效
   - 解压失败

建议使用 try-except 进行错误处理：
```python
try:
    crx_path = download_crx(url, output_dir)
    extract_dir = extract_crx(crx_path)
except ValueError as e:
    print(f"参数错误: {e}")
except RuntimeError as e:
    print(f"操作失败: {e}")
```

#### 日志记录

模块使用 Python 的 logging 模块记录操作日志：

- 日志文件: `crx_download.log`
- 日志格式: `%(asctime)s - %(levelname)s - %(message)s`
- 日志级别: INFO（默认）

可以通过以下方式调整日志级别：
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### 3. parser.py - 解析模块

负责解析和分析 CRX 文件内容。

```python
def parse_crx(crx_path: str) -> Dict[str, Any]:
    """
    解析 CRX 文件并提取信息
    
    Args:
        crx_path: CRX 文件路径
        
    Returns:
        dict: 包含 CRX 文件信息的字典
    """
```

## 开发指南

### 环境设置

1. 克隆项目：
```bash
git clone https://github.com/bineanzhou/crx-toolkit.git
cd crx-toolkit
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

### 运行测试

```bash
python -m pytest src/tests/
```

### 代码风格

- 遵循 PEP 8 规范
- 使用 Type Hints 进行类型注解
- 编写详细的文档字符串
- 保持函数简洁，单一职责

### 提交规范

提交信息格式：
```
<type>(<scope>): <subject>

<body>
```

类型（type）：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建过程或辅助工具的变动

### 发布流程

1. 更新版本号（src/crx_toolkit/__init__.py）
2. 更新 CHANGELOG.md
3. 创建发布标签
4. 构建并上传到 PyPI 