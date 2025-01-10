import requests
import os
import zipfile
import json
import re
from urllib.parse import urlparse, parse_qs, unquote
import logging
import argparse
import sys

def setup_logging(log_file='extension_download.log', debug=False):
    """配置日志"""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def setup_proxy(proxy):
    """设置代理"""
    if proxy:
        return {
            'http': proxy,
            'https': proxy,
        }
    return {}

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Chrome扩展下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s -u https://chromewebstore.google.com/detail/extension-id
  %(prog)s --url https://chromewebstore.google.com/detail/extension-id --proxy http://127.0.0.1:7890
  %(prog)s -u https://chromewebstore.google.com/detail/extension-id -d -o my_extensions
'''
    )
    
    parser.add_argument('-u', '--url', 
                      help='Chrome扩展的URL地址')
    parser.add_argument('-p', '--proxy',
                      help='代理服务器地址 (例如: http://127.0.0.1:7890)')
    parser.add_argument('-o', '--output',
                      default='extension_files',
                      help='输出目录 (默认: extension_files)')
    parser.add_argument('-d', '--debug',
                      action='store_true',
                      help='启用调试模式')
    parser.add_argument('-f', '--force',
                      action='store_true',
                      help='强制重新下载，即使文件已存在')
    parser.add_argument('--no-verify',
                      action='store_true',
                      help='禁用SSL验证')
    parser.add_argument('--timeout',
                      type=int,
                      default=30,
                      help='下载超时时间(秒)')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    return parser.parse_args()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extension_download.log'),
        logging.StreamHandler()
    ]
)

# 常量定义
DOWNLOAD_URLS = [
    # 格式1: Chrome Web Store API
    "https://clients2.google.com/service/update2/crx?response=redirect&acceptformat=crx2,crx3&prodversion=89.0.4389.90&x=id%3D{ID}%26installsource%3Dondemand%26uc",
    # 格式2: 备用API
    "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&x=id%3D{ID}%26installsource%3Dondemand%26uc",
    # 格式3: 简化格式
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

PROXIES = {
    # 'http': 'http://127.0.0.1:7890',
    # 'https': 'http://127.0.0.1:7890',
}

def extract_extension_id(url):
    """从Chrome网上应用店URL中提取扩展ID"""
    logging.info(f"开始从URL解析扩展ID: {url}")
    
    try:
        # 1. 尝试从URL路径中提取
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        # 处理不同的URL格式
        if 'detail' in path_parts:
            # 新版Chrome商店格式: /detail/name/id
            detail_index = path_parts.index('detail')
            if len(path_parts) > detail_index + 2:
                extension_id = path_parts[detail_index + 2]
            elif len(path_parts) > detail_index + 1:
                extension_id = path_parts[detail_index + 1]
            else:
                extension_id = None
        else:
            # 尝试直接从路径中找到ID格式的部分
            extension_id = next((part for part in path_parts if re.match(r'^[a-z]{32}$', part)), None)
        
        # 2. 如果路径中没有找到，尝试从查询参数中提取
        if not extension_id:
            query_params = parse_qs(parsed_url.query)
            if 'id' in query_params:
                extension_id = query_params['id'][0]
        
        # 3. 验证提取的ID是否符合格式
        if extension_id and re.match(r'^[a-z]{32}$', extension_id):
            logging.info(f"成功提取扩展ID: {extension_id}")
            return extension_id
        
        # 4. 如果上述方法都失败，尝试正则匹配
        patterns = [
            r'detail/[^/]+/([a-z]{32})',  # 匹配新版格式
            r'detail/([a-z]{32})',         # 匹配旧版格式
            r'([a-z]{32})'                 # 直接匹配ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                extension_id = match.group(1)
                logging.info(f"通过正则表达式提取到扩展ID: {extension_id}")
                return extension_id
        
        logging.error("无法从URL中提取有效的扩展ID")
        return None
        
    except Exception as e:
        logging.error(f"解析URL时出错: {str(e)}")
        return None

def try_download(url, timeout=30):
    """尝试从URL下载内容"""
    try:
        logging.info(f"正在尝试下载: {url}")
        response = requests.get(
            url, 
            headers=HEADERS, 
            proxies=PROXIES,
            timeout=timeout,
            allow_redirects=True,
            verify=False  # 如果有SSL证书问题，可以禁用验证
        )
        
        logging.info(f"状态码: {response.status_code}")
        if response.status_code == 200:
            content_length = len(response.content)
            logging.info(f"下载成功，内容长度: {content_length} bytes")
            if content_length > 1000:  # 确保文件大小至少为1KB
                return response
            else:
                logging.warning(f"文件太小 ({content_length} bytes)，可能不是有效的扩展文件")
        else:
            logging.warning(f"下载失败，HTTP状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logging.warning(f"请求异常: {str(e)}")
    except Exception as e:
        logging.warning(f"其他错误: {str(e)}")
    return None

def download_extension(args):
    """下载Chrome扩展"""
    if not args.url:
        logging.error("URL不能为空")
        return False
        
    logging.info(f"开始处理URL: {args.url}")
    
    # 提取扩展ID
    extension_id = extract_extension_id(args.url)
    if not extension_id:
        logging.error("扩展ID提取失败，终止下载")
        return False
    
    # 创建输出目录
    if not os.path.exists(args.output):
        logging.info(f"创建输出目录: {args.output}")
        os.makedirs(args.output)
    
    crx_path = os.path.join(args.output, f"{extension_id}.crx")
    zip_path = os.path.join(args.output, f"{extension_id}.zip")
    
    # 检查文件是否已存在
    if not args.force and os.path.exists(zip_path):
        logging.info(f"扩展文件已存在: {zip_path}")
        return True
    
    # 设置代理
    proxies = setup_proxy(args.proxy)
    
    # 尝试所有下载URL格式
    for url_template in DOWNLOAD_URLS:
        download_url = url_template.format(ID=extension_id)
        logging.info(f"尝试下载URL: {download_url}")
        
        try:
            response = requests.get(
                download_url,
                headers=HEADERS,
                proxies=proxies,
                timeout=args.timeout,
                allow_redirects=True,
                verify=not args.no_verify
            )
            
            if response.status_code == 200 and len(response.content) > 1000:
                # 保存和解压文件
                extract_dir = os.path.join(args.output, extension_id)
                
                try:
                    # 保存.crx文件
                    with open(crx_path, 'wb') as f:
                        f.write(response.content)
                    
                    # 转换为zip并解压
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                    os.rename(crx_path, zip_path)
                    
                    # 清理并创建解压目录
                    if os.path.exists(extract_dir):
                        import shutil
                        shutil.rmtree(extract_dir)
                    
                    # 解压文件
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    logging.info(f"扩展已成功下载并解压到: {extract_dir}")
                    return True
                    
                except Exception as e:
                    logging.error(f"处理文件时出错: {e}")
                    continue
                    
            else:
                logging.warning(f"下载失败或文件无效: {response.status_code}")
                
        except Exception as e:
            logging.warning(f"下载出错: {e}")
            continue
    
    logging.error("所有下载URL都失败")
    return False

def main():
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志
    setup_logging(debug=args.debug)
    
    # 下载扩展
    success = download_extension(args)
    
    # 设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 