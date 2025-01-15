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

负责从网络下载 CRX 文件。

```python
def download_crx(url: str, output_dir: str, filename: Optional[str] = None) -> str:
    """
    从指定 URL 下载 CRX 文件
    
    Args:
        url: CRX 文件的下载链接
        output_dir: 保存文件的目录
        filename: 可选的文件名
        
    Returns:
        str: 下载文件的保存路径
    """
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