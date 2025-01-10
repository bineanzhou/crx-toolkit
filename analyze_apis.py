import os
import json
import re
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extension_analysis.log'),
        logging.StreamHandler()
    ]
)

def analyze_manifest(manifest_path):
    """分析manifest.json中声明的权限和API"""
    logging.info(f"开始分析manifest文件: {manifest_path}")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        apis = set()
        
        # 检查permissions
        if 'permissions' in manifest:
            permissions = manifest['permissions']
            logging.info(f"找到权限声明: {permissions}")
            apis.update(permissions)
        
        # 检查optional_permissions
        if 'optional_permissions' in manifest:
            opt_permissions = manifest['optional_permissions']
            logging.info(f"找到可选权限声明: {opt_permissions}")
            apis.update(opt_permissions)
        
        logging.info(f"manifest分析完成，共找到 {len(apis)} 个API")
        return apis
        
    except FileNotFoundError:
        logging.error(f"找不到manifest文件: {manifest_path}")
        return set()
    except json.JSONDecodeError:
        logging.error(f"manifest.json 格式不正确")
        return set()
    except Exception as e:
        logging.error(f"分析manifest时出错: {e}")
        return set()

def analyze_js_files(directory):
    """分析JavaScript文件中使用的Chrome API"""
    logging.info(f"开始分析目录中的JS文件: {directory}")
    
    chrome_apis = set()
    pattern = r'chrome\.[a-zA-Z]+\.[a-zA-Z]+'
    
    if not os.path.exists(directory):
        logging.error(f"目录不存在: {directory}")
        return chrome_apis
    
    for root, dirs, files in os.walk(directory):
        js_files = [f for f in files if f.endswith('.js')]
        logging.info(f"在 {root} 中找到 {len(js_files)} 个JS文件")
        
        for file in js_files:
            file_path = os.path.join(root, file)
            logging.info(f"分析文件: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(pattern, content)
                    if matches:
                        logging.info(f"在 {file} 中找到 {len(matches)} 个Chrome API调用")
                        chrome_apis.update(matches)
            except Exception as e:
                logging.error(f"读取文件出错 {file_path}: {e}")
    
    logging.info(f"JS文件分析完成，共找到 {len(chrome_apis)} 个不同的Chrome API调用")
    return chrome_apis

def main():
    extension_dir = 'extension_files'
    manifest_path = os.path.join(extension_dir, 'manifest.json')
    
    logging.info("开始扩展分析")
    
    if not os.path.exists(extension_dir):
        logging.error(f"错误: 请先运行 download_extension.py 下载扩展")
        return
    
    # 分析manifest.json
    manifest_apis = analyze_manifest(manifest_path)
    if manifest_apis:
        print("\nmanifest.json中声明的API:")
        for api in sorted(manifest_apis):
            print(f"- {api}")
    
    # 分析JS文件
    js_apis = analyze_js_files(extension_dir)
    if js_apis:
        print("\nJavaScript文件中使用的Chrome API:")
        for api in sorted(js_apis):
            print(f"- {api}")
    
    logging.info("扩展分析完成")

if __name__ == "__main__":
    main() 