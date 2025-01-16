import os
import json
import logging
from typing import Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from .utils.file_utils import ensure_dir

def setup_logging(verbose: bool = False):
    """配置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('crx_pack.log'),
            logging.StreamHandler()
        ]
    )

def pack_extension(
    source_dir: str, 
    private_key_path: str, 
    output_dir: str, 
    force: bool = False,
    verbose: bool = False,
    no_verify: bool = False
) -> str:
    """打包 Chrome 扩展为 CRX 文件
    
    Args:
        source_dir: 扩展源目录路径
        private_key_path: 私钥文件路径
        output_dir: 输出目录路径
        force: 是否强制覆盖已存在的文件
        verbose: 是否启用详细日志
        no_verify: 是否跳过签名验证
    
    Returns:
        str: 生成的CRX文件路径
    """
    # 设置日志级别
    setup_logging(verbose)
    
    try:
        # 验证源目录
        if not os.path.isdir(source_dir):
            raise ValueError(f"源目录不存在: {source_dir}")
        logging.info(f"源目录验证通过: {source_dir}")
        
        # 读取 manifest.json
        manifest_path = os.path.join(source_dir, 'manifest.json')
        if not os.path.exists(manifest_path):
            raise ValueError(f"manifest.json 不存在: {manifest_path}")
            
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            logging.info(f"成功读取 manifest.json")
            logging.info(f"扩展信息:")
            logging.info(f"  名称: {manifest.get('name', 'Unknown')}")
            logging.info(f"  版本: {manifest.get('version', 'Unknown')}")
            logging.info(f"  描述: {manifest.get('description', 'No description')}")
        
        # 验证私钥文件
        if not os.path.exists(private_key_path):
            raise ValueError(f"私钥文件不存在: {private_key_path}")
        logging.info(f"私钥文件验证通过: {private_key_path}")
        
        # 读取私钥
        with open(private_key_path, 'rb') as f:
            try:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
                logging.info("成功加载私钥")
            except Exception as e:
                raise ValueError(f"私钥文件无效: {str(e)}")
        
        # 确保输出目录存在
        ensure_dir(output_dir)
        logging.info(f"输出目录准备完成: {output_dir}")
        
        # 构建输出文件名
        extension_name = manifest.get('name', '').replace(' ', '_')
        version = manifest.get('version', 'unknown')
        output_file = os.path.join(output_dir, f"{extension_name}-{version}.crx")
        
        # 检查是否需要强制覆盖
        if os.path.exists(output_file):
            if force:
                logging.warning(f"文件已存在，将被覆盖: {output_file}")
            else:
                raise FileExistsError(f"输出文件已存在: {output_file}")
        
        # 打包扩展文件
        logging.info("开始打包扩展...")
        
        # 收集文件列表
        files_to_pack = []
        excluded_patterns = ['.git', '.svn', '__pycache__', '*.pyc', '*.pyo', '*.pyd']
        for root, dirs, files in os.walk(source_dir):
            # 过滤目录
            dirs[:] = [d for d in dirs if not any(d.startswith(p.strip('*')) for p in excluded_patterns)]
            
            for file in files:
                # 过滤文件
                if any(file.endswith(p.strip('*')) for p in excluded_patterns):
                    continue
                    
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, source_dir)
                files_to_pack.append((rel_path, abs_path))
                if verbose:
                    logging.debug(f"添加文件: {rel_path}")
                    
        logging.info(f"找到 {len(files_to_pack)} 个文件需要打包")
        
        # 创建 ZIP 文件
        import zipfile
        zip_path = output_file + '.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for rel_path, abs_path in files_to_pack:
                zf.write(abs_path, rel_path)
        logging.info("ZIP 文件创建完成")
        
        # 读取 ZIP 内容
        with open(zip_path, 'rb') as f:
            zip_data = f.read()
        
        # 计算签名
        if not no_verify:
            signature = private_key.sign(
                zip_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            logging.info("签名计算完成")
            
            # 获取公钥
            public_key = private_key.public_key()
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.PKCS1
            )
            logging.info("公钥提取完成")
        else:
            logging.warning("跳过签名验证")
            signature = b''
            public_key_bytes = b''
        
        # 写入 CRX 文件
        with open(output_file, 'wb') as f:
            # CRX3 格式头部
            f.write(b'Cr24')  # Magic number
            f.write((3).to_bytes(4, byteorder='little'))  # Version
            f.write(len(public_key_bytes).to_bytes(4, byteorder='little'))
            f.write(len(signature).to_bytes(4, byteorder='little'))
            f.write(public_key_bytes)
            f.write(signature)
            f.write(zip_data)
        
        # 清理临时文件
        os.remove(zip_path)
        logging.info("临时文件清理完成")
        
        logging.info(f"扩展打包成功: {output_file}")
        return output_file
        
    except Exception as e:
        logging.error(f"打包失败: {str(e)}", exc_info=True)
        raise
    finally:
        # 清理可能存在的临时文件
        if 'zip_path' in locals() and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                logging.debug("清理临时ZIP文件")
            except:
                pass 