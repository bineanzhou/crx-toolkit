# CRX Toolkit API 文档

## 打包 API

### pack_extension()

```python
from crx_toolkit.packer import pack_extension

result = pack_extension(
    source_dir="./my_extension/",
    private_key_path="./private_key.pem",
    output_dir="./output/"
)
```

参数说明：
- source_dir: 扩展源目录路径
- private_key_path: 私钥文件路径
- output_dir: 输出目录路径

返回值：
- 生成的 CRX 文件路径

## 下载 API

### download_crx()

```python
from crx_toolkit.downloader import download_crx

result = download_crx(
    url="https://example.com/extension.crx",
    output_dir="./output/"
)
```

参数说明：
- url: CRX 文件的下载链接
- output_dir: 保存文件的目录
- filename: (可选) 自定义文件名

返回值：
- 下载文件的保存路径

## 解析 API

### parse_crx()

```python
from crx_toolkit.parser import parse_crx

result = parse_crx("./output/extension.crx")
print(result)
```

参数说明：
- crx_path: CRX 文件路径

返回值：
```python
{
    'format_version': str,
    'manifest': dict,
    'files': list,
    'size': int
}
```

## 工具函数

### file_utils

```python
from crx_toolkit.utils.file_utils import ensure_dir, clean_dir

# 确保目录存在
ensure_dir("./output/")

# 清理目录
clean_dir("./temp/")
```

### network_utils

```python
from crx_toolkit.utils.network_utils import download_file

# 下载文件
download_file(
    url="https://example.com/file.zip",
    output_path="./output/file.zip"
)
``` 