import os
from typing import Union, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import zipfile
import tempfile
import struct

def generate_private_key(output_path: str) -> None:
    """
    生成新的私钥
    
    Args:
        output_path: 保存私钥的路径
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    with open(output_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

def load_private_key(key_path: str) -> rsa.RSAPrivateKey:
    """
    加载私钥文件
    
    Args:
        key_path: 私钥文件路径
        
    Returns:
        RSAPrivateKey: 加载的私钥对象
    """
    with open(key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

def create_zip_file(source_dir: str) -> bytes:
    """
    将源目录打包为 ZIP 文件
    
    Args:
        source_dir: 源目录路径
        
    Returns:
        bytes: ZIP 文件的二进制内容
    """
    temp_zip = tempfile.NamedTemporaryFile(delete=False)
    try:
        with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, source_dir)
                    zf.write(file_path, arc_name)
        
        with open(temp_zip.name, 'rb') as f:
            return f.read()
    finally:
        os.unlink(temp_zip.name)

def sign_extension(source_dir: str, private_key_path: str) -> bytes:
    """
    签名并打包 Chrome 扩展
    
    Args:
        source_dir: 扩展源目录路径
        private_key_path: 私钥文件路径
        
    Returns:
        bytes: 签名后的 CRX 文件内容
    """
    # 加载私钥
    private_key = load_private_key(private_key_path)
    public_key = private_key.public_key()
    
    # 获取公钥的 DER 编码
    public_key_der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # 创建 ZIP 文件
    zip_data = create_zip_file(source_dir)
    
    # 签名 ZIP 数据
    signature = private_key.sign(
        zip_data,
        padding.PKCS1v15(),
        hashes.SHA1()
    )
    
    # CRX3 格式头部
    magic = b'Cr24'  # Chrome 扩展文件魔数
    version = struct.pack('<I', 3)  # CRX3 版本号
    header_size = struct.pack('<I', 4 + 4 + 4 + len(public_key_der) + len(signature))
    public_key_size = struct.pack('<I', len(public_key_der))
    signature_size = struct.pack('<I', len(signature))
    
    # 组装 CRX 文件
    crx_data = (
        magic +
        version +
        header_size +
        public_key_size +
        signature_size +
        public_key_der +
        signature +
        zip_data
    )
    
    return crx_data 