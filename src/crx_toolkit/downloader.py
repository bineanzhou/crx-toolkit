import os
import re
import json
import logging
import shutil
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs
import requests
import zipfile
from .utils.file_utils import ensure_dir
import tempfile
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S,%f',
    handlers=[
        logging.FileHandler('crx_download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 常量定义
DOWNLOAD_URLS = [
    # Chrome Web Store 直接下载链接
    "https://clients2.google.com/service/update2/crx?response=redirect&acceptformat=crx2,crx3&prodversion=102.0.5005.61&x=id%3D{ID}%26installsource%3Dondemand%26uc",
    "https://clients2.google.com/service/update2/crx?response=redirect&os=win&arch=x64&os_arch=x86_64&nacl_arch=x86-64&prod=chromecrx&prodchannel=&prodversion=102.0.5005.61&lang=zh-CN&acceptformat=crx3&x=id%3D{ID}%26installsource%3Dondemand%26uc",
    # 备用下载链接
    "https://dl.google.com/chrome/extensions/{ID}/{ID}.crx",
    "https://dl.google.com/chrome/extensions/{ID}/extension_{ID}.crx",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def extract_extension_id(url: str) -> Optional[str]:
    """从 URL 中提取扩展 ID
    
    支持的 URL 格式:
    1. Chrome Web Store 详情页: 
       - https://chrome.google.com/webstore/detail/name/id
       - https://chromewebstore.google.com/detail/name/id
    2. Chrome Web Store 主页:
       - https://chrome.google.com/webstore/detail/id
       - https://chromewebstore.google.com/detail/id
    3. 下载 URL:
       - https://clients2.google.com/service/update2/crx?...id%3Did...
    4. CRX 文件:
       - id.crx
    5. 纯 ID:
       - 32 位字母数字字符串
    
    Args:
        url: 扩展 URL 或 ID
        
    Returns:
        Optional[str]: 扩展 ID，如果无法提取则返回 None
    """
    # 移除引号和空白字符
    url = url.strip('"\'').strip()
    
    # 1. 检查是否是纯 ID（32位字母数字）
    if re.match(r'^[a-z]{32}$', url, re.IGNORECASE):
        return url.lower()
    
    # 2. Chrome Web Store URL 模式
    store_patterns = [
        # 新版详情页
        r'chromewebstore\.google\.com/detail/[^/]+/([a-z]{32})',
        r'chromewebstore\.google\.com/detail/([a-z]{32})',
        # 旧版详情页
        r'chrome\.google\.com/webstore/detail/[^/]+/([a-z]{32})',
        r'chrome\.google\.com/webstore/detail/([a-z]{32})',
    ]
    
    for pattern in store_patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    
    # 3. 下载 URL 模式
    if 'clients2.google.com' in url:
        # 尝试从查询参数中提取
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # 检查常见的 ID 参数
        id_params = ['id', 'x']
        for param in id_params:
            if param in query_params:
                value = query_params[param][0]
                # 处理编码的参数
                if '%3D' in value:
                    parts = value.split('%3D')
                    for part in parts:
                        if re.match(r'^[a-z]{32}$', part, re.IGNORECASE):
                            return part.lower()
                elif re.match(r'^[a-z]{32}$', value, re.IGNORECASE):
                    return value.lower()
    
    # 4. CRX 文件名模式
    crx_match = re.search(r'([a-z]{32})\.crx$', url, re.IGNORECASE)
    if crx_match:
        return crx_match.group(1).lower()
    
    # 5. 尝试查找任何位置的32位字母字符串
    id_match = re.search(r'(?<![a-z])([a-z]{32})(?![a-z])', url, re.IGNORECASE)
    if id_match:
        return id_match.group(1).lower()
    
    return None

def get_localized_name(manifest: dict, messages_dir: str) -> str:
    """获取本地化的扩展名称"""
    try:
        name = manifest.get('name', '')
        if not isinstance(name, str) or not name.startswith('__MSG_'):
            return name
            
        # 提取消息key
        msg_key = name[6:-2]  # 移除 '__MSG_' 和 '__'
        logging.info(f"查找本地化消息key: {msg_key}")
        
        # 按优先级查找本地化文件
        locales = ['zh_CN', 'en', 'en_US', 'default']
        for locale in locales:
            messages_file = os.path.join(messages_dir, locale, 'messages.json')
            if os.path.exists(messages_file):
                try:
                    with open(messages_file, 'r', encoding='utf-8') as f:
                        messages = json.load(f)
                        if msg_key in messages:
                            message = messages[msg_key]
                            if isinstance(message, dict):
                                localized_name = message.get('message', '')
                                if localized_name:
                                    logging.info(f"找到本地化名称[{locale}]: {localized_name}")
                                    return localized_name
                except Exception as e:
                    logging.warning(f"读取本地化文件失败[{locale}]: {e}")
                    continue
                    
        logging.warning(f"未找到本地化消息: {msg_key}")
        return name
        
    except Exception as e:
        logging.error(f"获取本地化名称失败: {e}")
        return name

def parse_crx_header(crx_path: str) -> Tuple[bytes, bytes, bytes]:
    """解析 CRX 文件头
    
    Args:
        crx_path: CRX 文件路径
        
    Returns:
        Tuple[bytes, bytes, bytes]: (签名, 公钥, ZIP数据)
    """
    with open(crx_path, 'rb') as f:
        data = f.read()
        
        # 策略1: 直接查找 ZIP 文件头
        zip_start = data.find(b'PK\x03\x04')
        if zip_start != -1:
            logging.info(f"找到 ZIP 文件头（偏移量: {zip_start}）")
            return b'', b'', data[zip_start:]
        
        # 策略2: 尝试解析 CRX 头部
        try:
            f.seek(0)
            magic = f.read(4)
            
            # 如果不是标准的 CRX 头部，尝试其他偏移量
            if magic != b'Cr24':
                # 尝试不同的偏移量
                for offset in [0, 4, 8, 12, 16]:
                    f.seek(offset)
                    data_slice = f.read()
                    zip_start = data_slice.find(b'PK\x03\x04')
                    if zip_start != -1:
                        logging.info(f"在偏移量 {offset + zip_start} 处找到 ZIP 文件头")
                        return b'', b'', data_slice[zip_start:]
                
                # 如果所有尝试都失败，返回原始数据
                logging.warning("未找到标准的 CRX 头部或 ZIP 文件头，尝试直接使用文件内容")
                return b'', b'', data
            
            # 标准 CRX 格式处理
            version = int.from_bytes(f.read(4), byteorder='little')
            logging.info(f"检测到 CRX 版本: {version}")
            
            if version == 2:
                header_length = int.from_bytes(f.read(4), byteorder='little')
                signature_length = int.from_bytes(f.read(4), byteorder='little')
                
                # 合理性检查
                if 0 < header_length < 10000 and 0 < signature_length < 10000:
                    f.seek(16)  # 重置到数据开始位置
                    remaining_data = f.read()
                    zip_start = remaining_data.find(b'PK\x03\x04')
                    if zip_start != -1:
                        return b'', b'', remaining_data[zip_start:]
            
            elif version == 3:
                header_length = int.from_bytes(f.read(4), byteorder='little')
                if 0 < header_length < 10000:
                    f.seek(12)  # 重置到数据开始位置
                    remaining_data = f.read()
                    zip_start = remaining_data.find(b'PK\x03\x04')
                    if zip_start != -1:
                        return b'', b'', remaining_data[zip_start:]
            
            # 如果标准解析失败，尝试查找 ZIP 文件头
            f.seek(0)
            data = f.read()
            zip_start = data.find(b'PK\x03\x04')
            if zip_start != -1:
                logging.info(f"通过备用方法在偏移量 {zip_start} 处找到 ZIP 文件头")
                return b'', b'', data[zip_start:]
            
            # 如果还是找不到，返回原始数据
            logging.warning("无法找到有效的 ZIP 数据，尝试直接使用文件内容")
            return b'', b'', data
            
        except Exception as e:
            logging.warning(f"解析 CRX 头部时出错: {str(e)}")
            # 发生错误时，尝试直接返回数据
            return b'', b'', data

def get_crx_info(crx_path: str) -> Tuple[str, str]:
    """从 CRX 文件中获取扩展信息
    
    Args:
        crx_path: CRX 文件路径
        
    Returns:
        Tuple[str, str]: (扩展名称, 版本号)
    """
    temp_dir = os.path.join(os.path.dirname(crx_path), '_temp_extract')
    try:
        logging.info(f"创建临时目录: {temp_dir}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # 解析 CRX 文件
        try:
            _, _, zip_data = parse_crx_header(crx_path)
            
            # 保存 ZIP 数据到临时文件
            temp_zip = os.path.join(temp_dir, 'temp.zip')
            with open(temp_zip, 'wb') as f:
                f.write(zip_data)
                
            # 解压 ZIP 文件
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
        except Exception as e:
            logging.warning(f"直接解压失败: {str(e)}")
            # 如果解析失败，尝试跳过文件头直接解压
            try:
                with open(crx_path, 'rb') as f:
                    # 跳过 CRX 头部
                    f.seek(16)  # 跳过魔数(4) + 版本(4) + 两个长度字段(4+4)
                    data = f.read()
                    
                # 尝试在数据中查找 ZIP 文件头
                zip_start = data.find(b'PK\x03\x04')
                if zip_start == -1:
                    raise ValueError("找不到 ZIP 文件头")
                    
                # 保存 ZIP 数据到临时文件
                temp_zip = os.path.join(temp_dir, 'temp.zip')
                with open(temp_zip, 'wb') as f:
                    f.write(data[zip_start:])
                    
                # 解压 ZIP 文件
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
            except Exception as e:
                logging.error(f"备用解压方法也失败: {str(e)}")
                return None, None
        
        # 读取 manifest.json
        manifest_path = os.path.join(temp_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            raise ValueError("manifest.json 不存在")
            
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            logging.info("成功读取manifest.json")
            
            # 获取扩展名称
            name = manifest.get('name', '')
            
            # 处理本地化消息
            if isinstance(name, str) and name.startswith('__MSG_'):
                locales_dir = os.path.join(temp_dir, '_locales')
                name = get_localized_name(manifest, locales_dir)
            elif isinstance(name, dict):  # 处理多语言名称
                name = name.get('default') or name.get('en') or name.get('zh_CN') or next(iter(name.values()))
            
            # 获取版本号
            version = manifest.get('version', 'unknown')
            
            # 清理名称
            name = str(name).strip()
            name = re.sub(r'[<>:"/\\|?*]', '-', name)
            name = name.strip('-.')
            
            if not name:
                raise ValueError("未找到有效的扩展名称")
                
            logging.info(f"从manifest获取信息 - 名称: {name}, 版本: {version}")
            return name, version
            
    except Exception as e:
        logging.error(f"解析CRX文件失败: {str(e)}", exc_info=True)
        return None, None
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.debug("清理临时目录")
        except Exception as e:
            logging.warning(f"清理临时目录失败: {e}")

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除或替换非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 替换 Windows 下的非法字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 移除控制字符
    filename = ''.join(char for char in filename if ord(char) >= 32)
    
    # 确保文件名不为空
    if not filename:
        filename = 'extension'
    
    return filename

def download_crx(
    url: str,
    output_dir: str,
    force: bool = True,
    verbose: bool = False,
    no_verify: bool = False
) -> str:
    """下载 Chrome 扩展 CRX 文件
    
    Args:
        url: 扩展下载链接
        output_dir: 输出目录路径
        force: 是否强制覆盖已存在的文件
        verbose: 是否启用详细日志
        no_verify: 是否跳过签名验证
    
    Returns:
        str: 下载的CRX文件路径
    """
    try:
        # 验证URL和输出目录
        if not url:
            raise ValueError("下载链接不能为空")
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 从URL中提取扩展ID
        extension_id = extract_extension_id(url)
        if not extension_id:
            raise ValueError("无法从URL中提取扩展ID")
        
        logging.info(f"检测到扩展ID: {extension_id}")
        
        # 构建并尝试所有可能的下载URL
        download_urls = [template.format(ID=extension_id) for template in DOWNLOAD_URLS]
        # 添加原始URL作为最后的备选
        if url not in download_urls:
            download_urls.append(url)
        
        last_error = None
        for download_url in download_urls:
            try:
                logging.info(f"尝试下载链接: {download_url}")
                # 先用HEAD请求检查URL是否可用
                response = requests.head(download_url, headers=HEADERS, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    # 创建临时目录用于下载文件
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_file = os.path.join(temp_dir, 'temp.crx')
                        
                        # 下载文件
                        logging.info(f"开始从 {download_url} 下载扩展...")
                        response = requests.get(download_url, headers=HEADERS, stream=True, timeout=30)
                        response.raise_for_status()
                        
                        # 检查是否是有效的响应
                        content_type = response.headers.get('content-type', '')
                        if 'html' in content_type.lower():
                            logging.warning(f"跳过HTML响应: {download_url}")
                            continue
                        
                        # 保存文件
                        with open(temp_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        # 验证下载的文件
                        if os.path.getsize(temp_file) < 100:  # 文件太小，可能不是有效的CRX
                            logging.warning(f"下载的文件太小，可能不是有效的CRX: {os.path.getsize(temp_file)} bytes")
                            continue
                        
                        # 尝试解析CRX头部，验证文件有效性
                        try:
                            with open(temp_file, 'rb') as f:
                                magic = f.read(4)
                                if magic == b'Cr24' or b'PK\x03\x04' in magic:
                                    logging.info("验证成功：文件包含有效的CRX或ZIP头")
                                else:
                                    logging.warning("文件不是有效的CRX格式，尝试下一个链接")
                                    continue
                        except Exception as e:
                            logging.warning(f"文件格式验证失败: {e}")
                            continue
                        
                        # 先使用临时文件名保存
                        temp_output = os.path.join(output_dir, f"{extension_id}_temp.crx")
                        os.makedirs(os.path.dirname(temp_output), exist_ok=True)
                        shutil.copy2(temp_file, temp_output)
                        
                        # 尝试从CRX文件获取信息
                        name, version = get_crx_info(temp_output)
                        
                        # 构建最终文件名
                        if name and version:
                            # 使用扩展名和版本号
                            filename = f"{name}-{version}"
                        else:
                            filename = extension_id
                        
                        # 清理并规范化文件名
                        filename = sanitize_filename(filename)
                        if len(filename) > 200:  # 预留.crx扩展名和一些余量
                            filename = filename[:197] + "..."
                        
                        # 添加.crx扩展名
                        final_output = os.path.join(output_dir, f"{filename}.crx")
                        
                        # 处理文件已存在的情况
                        if os.path.exists(final_output) and final_output != temp_output:
                            if force:
                                logging.warning(f"文件已存在，将被覆盖: {final_output}")
                                try:
                                    os.remove(final_output)
                                except Exception as e:
                                    logging.warning(f"删除已存在的文件失败: {str(e)}")
                            else:
                                # 如果不允许覆盖，添加数字后缀
                                counter = 1
                                while os.path.exists(final_output):
                                    new_filename = f"{filename}_{counter}.crx"
                                    final_output = os.path.join(output_dir, new_filename)
                                    counter += 1
                                logging.info(f"文件已存在，使用新文件名: {os.path.basename(final_output)}")
                        
                        # 重命名临时文件为最终文件名
                        try:
                            shutil.move(temp_output, final_output)
                            logging.info(f"扩展下载成功: {final_output}")
                            return final_output
                        except Exception as e:
                            logging.error(f"重命名文件失败: {str(e)}")
                            return temp_output
                            
            except requests.RequestException as e:
                last_error = e
                logging.warning(f"下载失败 {download_url}: {str(e)}")
                continue
        
        # 如果所有URL都尝试失败
        raise RuntimeError(f"所有下载链接均失败，最后的错误: {str(last_error)}")
        
    except Exception as e:
        logging.error(f"下载失败: {str(e)}", exc_info=True)
        raise

def extract_crx(crx_path: str, extract_dir: Optional[str] = None) -> str:
    """解压 CRX 文件
    
    Args:
        crx_path: CRX 文件路径
        extract_dir: 解压目录路径，如果不指定则使用扩展名作为目录名
        
    Returns:
        str: 解压后的目录路径
    """
    try:
        # 获取扩展信息
        name, version = get_crx_info(crx_path)
        
        if not extract_dir:
            if name:
                # 使用扩展名作为解压目录
                extract_dir = os.path.join(os.path.dirname(crx_path), name)
            else:
                # 如果无法获取扩展名，使用文件名（不含扩展名）
                base_name = os.path.splitext(os.path.basename(crx_path))[0]
                extract_dir = os.path.join(os.path.dirname(crx_path), base_name)
        
        ensure_dir(extract_dir)
        
        # 解析 CRX 文件
        try:
            _, _, zip_data = parse_crx_header(crx_path)
            
            # 保存 ZIP 数据到临时文件
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(zip_data)
                temp_zip = temp_file.name
                
            # 解压 ZIP 文件
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # 删除临时文件
            os.unlink(temp_zip)
            
        except Exception as e:
            logging.warning(f"直接解压失败，尝试备用方法: {str(e)}")
            # 如果解析失败，尝试跳过文件头直接解压
            try:
                with open(crx_path, 'rb') as f:
                    # 跳过 CRX 头部
                    f.seek(16)  # 跳过魔数(4) + 版本(4) + 两个长度字段(4+4)
                    data = f.read()
                    
                # 尝试在数据中查找 ZIP 文件头
                zip_start = data.find(b'PK\x03\x04')
                if zip_start == -1:
                    raise ValueError("找不到 ZIP 文件头")
                    
                # 保存 ZIP 数据到临时文件
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(data[zip_start:])
                    temp_zip = temp_file.name
                    
                # 解压 ZIP 文件
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    
                # 删除临时文件
                os.unlink(temp_zip)
                
            except Exception as e:
                raise RuntimeError(f"解压失败: {str(e)}")
        
        # 读取manifest.json获取更多信息
        manifest_path = os.path.join(extract_dir, 'manifest.json')
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                logging.info(f"扩展信息:")
                logging.info(f"  名称: {manifest.get('name', 'Unknown')}")
                logging.info(f"  版本: {manifest.get('version', 'Unknown')}")
                logging.info(f"  描述: {manifest.get('description', 'No description')}")
        
        logging.info(f"CRX文件已解压到: {extract_dir}")
        return extract_dir
        
    except Exception as e:
        raise RuntimeError(f"解压失败: {str(e)}") 