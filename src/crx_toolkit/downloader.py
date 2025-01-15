import os
import re
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import requests
import zipfile
from .utils.file_utils import ensure_dir

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crx_download.log'),
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

def download_crx(url: str, output_dir: str, proxy: Optional[str] = None) -> str:
    """下载 CRX 文件"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 提取扩展 ID
    extension_id = extract_extension_id(url)
    if not extension_id:
        raise ValueError("无法从 URL 中提取扩展 ID")
    
    # 设置代理
    proxies = {}
    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy
        }
    
    # 尝试所有下载 URL
    for template in DOWNLOAD_URLS:
        try:
            download_url = template.format(ID=extension_id)
            response = requests.get(
                download_url,
                headers=HEADERS,
                proxies=proxies,
                timeout=30,
                verify=True
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                # 使用扩展 ID 作为文件名
                output_path = os.path.join(output_dir, f"{extension_id}.crx")
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 保存文件
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                    
                return os.path.relpath(output_path, output_dir)
                
        except Exception as e:
            logging.warning(f"尝试下载失败: {str(e)}")
            continue
            
    raise RuntimeError("所有下载尝试均失败")

def extract_crx(crx_path: str, extract_dir: Optional[str] = None) -> str:
    """
    解压 CRX 文件
    
    Args:
        crx_path: CRX 文件路径
        extract_dir: 可选的解压目录，默认使用同名目录
        
    Returns:
        str: 解压目录路径
    """
    if not extract_dir:
        extract_dir = os.path.splitext(crx_path)[0]
    
    ensure_dir(extract_dir)
    
    try:
        with zipfile.ZipFile(crx_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        logging.info(f"CRX文件已解压到: {extract_dir}")
        return extract_dir
    except Exception as e:
        raise RuntimeError(f"解压失败: {str(e)}") 