#!/usr/bin/env python3

import os
import sys
import json
from PIL import Image
import argparse

ICON_SIZES = [16, 32, 48, 128]

def convert_icon(source_image_path, output_dir):
    """将源图片转换为Chrome扩展所需的各种尺寸的图标"""
    try:
        # 打开源图片
        with Image.open(source_image_path) as img:
            # 确保图片是RGBA模式
            img = img.convert('RGBA')
            
            # 创建输出目录
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            icon_paths = {}
            # 生成不同尺寸的图标
            for size in ICON_SIZES:
                output_filename = f'icon{size}.png'
                output_path = os.path.join(output_dir, output_filename)
                
                # 调整图片大小并保持纵横比
                resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                resized_img.save(output_path, 'PNG')
                
                # 记录相对路径，包含 icons 目录
                icon_paths[str(size)] = f"icons/{output_filename}"
            
            return icon_paths
    except Exception as e:
        print(f'Error converting icon: {str(e)}')
        return None

def update_manifest(manifest_path, icon_paths):
    """更新manifest.json文件中的图标配置"""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # 更新图标配置
        manifest['icons'] = icon_paths
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f'Error updating manifest: {str(e)}')
        return False

def convert_crx_icon(source_image=None, extension_dir=None):
    if source_image is None or extension_dir is None:
        parser = argparse.ArgumentParser(description='Convert images to Chrome extension icons')
        parser.add_argument('source_image', help='Source image file path')
        parser.add_argument('extension_dir', help='Extension directory path')
        
        args = parser.parse_args()
        source_image = args.source_image
        extension_dir = args.extension_dir
    
    # 验证输入
    if not os.path.isfile(source_image):
        print(f'Error: Source image {source_image} does not exist')
        sys.exit(1)
    
    if not os.path.isdir(extension_dir):
        print(f'Error: Extension directory {extension_dir} does not exist')
        sys.exit(1)
    
    manifest_path = os.path.join(extension_dir, 'manifest.json')
    if not os.path.isfile(manifest_path):
        print(f'Error: manifest.json not found in {extension_dir}')
        sys.exit(1)
    
    # 转换图标
    icons_dir = os.path.join(extension_dir, 'icons')
    icon_paths = convert_icon(source_image, icons_dir)
    
    if not icon_paths:
        print('Icon conversion failed')
        sys.exit(1)
    
    # 更新manifest.json
    if not update_manifest(manifest_path, icon_paths):
        print('Failed to update manifest.json')
        sys.exit(1)
    
    print('Icon conversion completed successfully')

if __name__ == '__main__':
    convert_crx_icon()