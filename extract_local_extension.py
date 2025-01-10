import os
import shutil
import json
import logging

def find_local_extension(extension_id):
    """从Chrome本地文件系统查找扩展"""
    # Chrome扩展的可能位置
    possible_paths = [
        # Windows
        os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions'),
        # Linux
        os.path.expanduser('~/.config/google-chrome/Default/Extensions'),
        # macOS
        os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Extensions'),
    ]
    
    for base_path in possible_paths:
        ext_path = os.path.join(base_path, extension_id)
        if os.path.exists(ext_path):
            # 获取最新版本
            versions = os.listdir(ext_path)
            if versions:
                latest_version = sorted(versions)[-1]
                return os.path.join(ext_path, latest_version)
    
    return None

def copy_local_extension(extension_id, dest_dir='extension_files'):
    """复制本地扩展文件"""
    src_path = find_local_extension(extension_id)
    if not src_path:
        logging.error("未找到本地扩展文件")
        return False
        
    dest_path = os.path.join(dest_dir, extension_id)
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        shutil.copytree(src_path, dest_path)
        logging.info(f"成功复制扩展到: {dest_path}")
        return True
    except Exception as e:
        logging.error(f"复制扩展文件失败: {e}")
        return False

# 使用方法
extension_id = "hniebljpgcogalllopnjokppmgbhaden"
copy_local_extension(extension_id) 