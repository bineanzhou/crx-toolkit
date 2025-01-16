import os
import re
import json
import logging
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs
import requests
import zipfile
from .utils.file_utils import ensure_dir

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crx_download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 常量定义
DOWNLOAD_URLS = [
    # Chrome Web Store API 格式
    "https://clients2.google.com/service/update2/crx?response=redirect&acceptformat=crx2,crx3&prodversion=89.0.4389.90&x=id%3D{ID}%26installsource%3Dondemand%26uc",
    # 备用 API 格式
    "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&x=id%3D{ID}%26installsource%3Dondemand%26uc",
    # 简化格式
    "https://clients2.google.com/service/update2/crx?response=redirect&x=id%3D{ID}%26uc",
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
    """从 URL 中提取扩展 ID"""
    # 移除引号（如果存在）
    url = url.strip('"\'')
    
    # Chrome Web Store URL 模式
    patterns = [
        r'chrome\.google\.com/webstore/detail/[^/]+/([a-z]{32})',
        r'chromewebstore\.google\.com/detail/[^/]+/([a-z]{32})',
        r'clients2\.google\.com/service/update2/crx\?.*?%3D([a-z]{32})',
        r'/([a-z]{32})\.crx$',
        r'([a-z]{32})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 如果是完整的 ID（32位字母）
    if re.match(r'^[a-z]{32}$', url):
        return url
        
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

def get_crx_info(crx_path: str) -> Tuple[str, str]:
    """从CRX文件中获取扩展信息"""
    try:
        # 创建临时目录
        temp_dir = os.path.join(os.path.dirname(crx_path), "_temp_extract")
        os.makedirs(temp_dir, exist_ok=True)
        logging.info(f"创建临时目录: {temp_dir}")
        
        manifest_file = None
        try:
            # 尝试直接作为zip文件解压
            with zipfile.ZipFile(crx_path, 'r') as zip_ref:
                # 解压manifest.json和_locales目录
                for file in zip_ref.namelist():
                    if file.endswith('manifest.json') or file.startswith('_locales/'):
                        zip_ref.extract(file, temp_dir)
                        if file.endswith('manifest.json'):
                            manifest_file = file
                logging.info(f"成功解压manifest和本地化文件")
                
        except Exception as e:
            logging.warning(f"直接解压失败: {e}")
            # 如果直接解压失败，尝试跳过CRX头部
            with open(crx_path, 'rb') as f:
                # 跳过CRX头部(通常是4-12字节)
                magic = f.read(4)  # CRX magic number
                if magic == b'Cr24':
                    version = int.from_bytes(f.read(4), byteorder='little')
                    if version == 2:
                        f.seek(16)  # Skip public key and signature lengths
                    elif version == 3:
                        f.seek(12)  # Skip signed header size
                    else:
                        f.seek(8)  # Default offset
                else:
                    f.seek(0)  # Reset if not a CRX file
                
                # 读取剩余内容并解压
                zip_data = f.read()
                temp_zip = os.path.join(temp_dir, "temp.zip")
                with open(temp_zip, 'wb') as zip_file:
                    zip_file.write(zip_data)
                
                with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                    for file in zip_ref.namelist():
                        if file.endswith('manifest.json') or file.startswith('_locales/'):
                            zip_ref.extract(file, temp_dir)
                            if file.endswith('manifest.json'):
                                manifest_file = file
                    logging.info(f"通过跳过头部方式成功解压文件")
        
        if not manifest_file:
            raise ValueError("未找到manifest.json文件")
            
        # 读取manifest.json
        manifest_path = os.path.join(temp_dir, manifest_file)
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
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            logging.debug("清理临时目录")
        except Exception as e:
            logging.warning(f"清理临时目录失败: {e}")

def download_crx(url: str, output_dir: str, proxy: Optional[str] = None) -> str:
    """下载 CRX 文件"""
    try:
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 提取扩展 ID
        extension_id = extract_extension_id(url)
        if not extension_id:
            raise ValueError("无法从 URL 中提取扩展 ID")
        
        logging.info(f"开始下载扩展 ID: {extension_id}")
        
        # 先使用临时文件名下载
        temp_file = os.path.join(output_dir, f"{extension_id}_temp.crx")
        
        # 设置代理
        proxies = {}
        if proxy:
            proxies = {'http': proxy, 'https': proxy}
            logging.info(f"使用代理: {proxy}")
        
        # 尝试所有下载 URL
        downloaded = False
        for template in DOWNLOAD_URLS:
            try:
                download_url = template.format(ID=extension_id)
                logging.info(f"尝试下载: {download_url}")
                
                response = requests.get(
                    download_url,
                    headers=HEADERS,
                    proxies=proxies,
                    timeout=30,
                    verify=True
                )
                
                if response.status_code == 200 and len(response.content) > 1000:
                    # 保存临时文件
                    with open(temp_file, 'wb') as f:
                        f.write(response.content)
                    logging.info(f"下载成功，临时文件: {temp_file}")
                    downloaded = True
                    break
                    
            except Exception as e:
                logging.warning(f"尝试下载失败: {str(e)}")
                continue
        
        if not downloaded:
            raise RuntimeError("所有下载尝试均失败")
        
        # 从CRX文件获取信息
        name, version = get_crx_info(temp_file)
        if name and version:
            # 使用获取到的信息重命名文件
            final_name = f"{name}-{version}.crx"
            final_path = os.path.join(output_dir, final_name)
            os.rename(temp_file, final_path)
            logging.info(f"文件已重命名: {final_name}")
            return os.path.relpath(final_path, output_dir)
        else:
            # 如果获取信息失败，使用ID作为名称
            final_name = f"{extension_id}.crx"
            final_path = os.path.join(output_dir, final_name)
            os.rename(temp_file, final_path)
            logging.warning(f"未能获取扩展信息，使用ID命名: {final_name}")
            return os.path.relpath(final_path, output_dir)
            
    except Exception as e:
        logging.error(f"下载失败: {str(e)}", exc_info=True)
        # 清理临时文件
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return ""

def extract_crx(crx_path: str, extract_dir: Optional[str] = None) -> str:
    """解压 CRX 文件"""
    if not extract_dir:
        # 使用不带版本号的扩展名作为解压目录
        base_name = os.path.splitext(os.path.basename(crx_path))[0]
        extension_name = base_name.rsplit('-', 1)[0]  # 移除版本号部分
        extract_dir = os.path.join(os.path.dirname(crx_path), extension_name)
    
    ensure_dir(extract_dir)
    
    try:
        with zipfile.ZipFile(crx_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
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