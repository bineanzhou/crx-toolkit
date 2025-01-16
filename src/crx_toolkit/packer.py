import os
import json
import logging
import subprocess
import tempfile
import zipfile
from typing import Optional, List, Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from .utils.file_utils import ensure_dir

def setup_logging(verbose: bool = False, log_file: str = 'crx_pack.log'):
    """配置日志
    
    Args:
        verbose: 是否启用详细日志
        log_file: 日志文件名
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def get_node_path() -> str:
    """获取 Node.js 可执行文件路径"""
    try:
        # Windows 系统
        if os.name == 'nt':
            # 检查常见安装路径
            common_paths = [
                os.path.expandvars(r'%ProgramFiles%\nodejs\node.exe'),
                os.path.expandvars(r'%ProgramFiles(x86)%\nodejs\node.exe'),
                os.path.expandvars(r'%APPDATA%\npm\node.exe'),
                # 添加其他可能的安装路径
            ]
            
            # 首先检查 PATH 环境变量
            if 'PATH' in os.environ:
                for path in os.environ['PATH'].split(os.pathsep):
                    node_exe = os.path.join(path.strip('"'), 'node.exe')
                    if os.path.isfile(node_exe):
                        return node_exe
            
            # 然后检查常见安装路径
            for path in common_paths:
                if os.path.isfile(path):
                    return path
                    
        # Linux/Mac 系统
        else:
            # 使用 which 命令查找
            try:
                result = subprocess.run(['which', 'node'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
                
            # 检查常见安装路径
            common_paths = [
                '/usr/bin/node',
                '/usr/local/bin/node',
                '/opt/node/bin/node'
            ]
            for path in common_paths:
                if os.path.isfile(path):
                    return path
                    
        return 'node'  # 如果找不到，返回默认命令
    except Exception as e:
        logging.debug(f"查找 Node.js 路径时发生错误: {str(e)}")
        return 'node'

def check_nodejs_installed() -> bool:
    """检查 Node.js 和 npm 是否已安装"""
    try:
        node_path = get_node_path()
        npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
        
        # 检查 node 版本
        node_result = subprocess.run(
            [node_path, '--version'], 
            capture_output=True, 
            text=True,
            env=os.environ.copy()  # 使用当前环境变量
        )
        if node_result.returncode != 0:
            logging.error("Node.js 未安装，请先安装 Node.js: https://nodejs.org/")
            return False
            
        # 检查 npm 版本
        npm_result = subprocess.run(
            [npm_cmd, '--version'],
            capture_output=True,
            text=True,
            env=os.environ.copy()  # 使用当前环境变量
        )
        if npm_result.returncode != 0:
            logging.error("npm 未安装或损坏，请重新安装 Node.js")
            return False
            
        logging.info(f"检测到 Node.js {node_result.stdout.strip()} 和 npm {npm_result.stdout.strip()}")
        return True
    except FileNotFoundError:
        logging.error("Node.js 未安装，请先安装 Node.js: https://nodejs.org/")
        return False
    except Exception as e:
        logging.error(f"检查 Node.js 时发生错误: {str(e)}")
        return False

def install_terser() -> bool:
    """安装 terser"""
    try:
        # 首先检查 Node.js 环境
        if not check_nodejs_installed():
            return False
            
        logging.info("正在安装 terser...")
        npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
        
        # 确保在项目目录中有 package.json
        if not os.path.exists('package.json'):
            logging.info("初始化 package.json...")
            init_result = subprocess.run(
                [npm_cmd, 'init', '-y'],
                capture_output=True,
                text=True,
                check=False,
                env=os.environ.copy()  # 使用当前环境变量
            )
            if init_result.returncode != 0:
                logging.error(f"初始化 package.json 失败: {init_result.stderr}")
                return False
        
        # 安装 terser
        result = subprocess.run(
            [npm_cmd, 'install', 'terser', '--save-dev'],
            capture_output=True,
            text=True,
            check=False,
            env=os.environ.copy()  # 使用当前环境变量
        )
        
        if result.returncode == 0:
            logging.info("terser 安装成功")
            return True
        else:
            logging.error(f"terser 安装失败: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"安装 terser 时发生错误: {str(e)}")
        return False

def check_terser_installed() -> bool:
    """检查 terser 是否已安装"""
    try:
        # 首先检查 Node.js 环境
        if not check_nodejs_installed():
            return False
            
        # 检查本地安装的 terser
        npx_cmd = 'npx.cmd' if os.name == 'nt' else 'npx'
        result = subprocess.run(
            [npx_cmd, 'terser', '--version'], 
            capture_output=True, 
            text=True,
            check=False,
            env=os.environ.copy()  # 使用当前环境变量
        )
        
        if result.returncode == 0:
            logging.info(f"检测到 terser 版本: {result.stdout.strip()}")
            return True
            
        # 如果 npx 检查失败，尝试直接检查全局安装的 terser
        terser_cmd = 'terser.cmd' if os.name == 'nt' else 'terser'
        result = subprocess.run(
            [terser_cmd, '--version'],
            capture_output=True,
            text=True,
            check=False,
            env=os.environ.copy()
        )
        
        if result.returncode == 0:
            logging.info(f"检测到全局安装的 terser 版本: {result.stdout.strip()}")
            return True
            
        return False
    except Exception as e:
        logging.error(f"检查 terser 时发生错误: {str(e)}")
        return False

def ensure_terser_available() -> bool:
    """确保 terser 可用，如果未安装则尝试安装"""
    if check_terser_installed():
        return True
        
    logging.info("terser 未安装，尝试自动安装...")
    if install_terser():
        return check_terser_installed()
    return False

def minify_js_file(input_path: str, output_path: str) -> bool:
    """使用 terser 混淆 JavaScript 文件"""
    try:
        # 构建 terser 命令
        npx_cmd = 'npx.cmd' if os.name == 'nt' else 'npx'
        cmd = [
            npx_cmd, 'terser', input_path,
            '--compress', 'passes=3,pure_funcs=[console.log],drop_console=true,'
                        'unsafe=true,dead_code=true,toplevel=true,evaluate=true',
            '--mangle', 'toplevel=true,eval=true,reserved=[chrome,browser]',
            '--format', 'comments=false,beautify=false',
            '--output', output_path
        ]
        
        # 运行 terser
        result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
        
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            orig_size = os.path.getsize(input_path)
            new_size = os.path.getsize(output_path)
            saved = ((orig_size - new_size) / orig_size) * 100
            logging.info(f"混淆 {os.path.basename(input_path)}: {orig_size} -> {new_size} 字节 (减少 {saved:.1f}%)")
            return True
            
        if result.stderr:
            logging.warning(f"混淆失败输出: {result.stderr}")
        return False
        
    except subprocess.CalledProcessError as e:
        logging.warning(f"混淆 {input_path} 失败: {e.stderr if e.stderr else str(e)}")
        return False
    except Exception as e:
        logging.warning(f"混淆 {input_path} 时发生错误: {str(e)}")
        return False

def pack_extension(
    source_dir: str, 
    private_key_path: Optional[str], 
    output_dir: str, 
    force: bool = True,
    verbose: bool = False,
    no_verify: bool = False,
    use_terser: bool = False,
    use_zip: bool = False
) -> str:
    """打包 Chrome 扩展
    
    Args:
        source_dir: 扩展源目录路径
        private_key_path: 私钥文件路径，如果为None则打包为zip格式
        output_dir: 输出目录路径
        force: 是否强制覆盖已存在的文件
        verbose: 是否启用详细日志
        no_verify: 是否跳过签名验证
        use_terser: 是否使用 terser 混淆 JavaScript 代码
        use_zip: 是否使用zip格式打包
    
    Returns:
        str: 生成的文件路径
    """
    # 设置日志配置
    setup_logging(verbose=verbose, log_file='crx_pack.log')
    
    try:
        # 如果启用了terser，确保其可用
        terser_available = False
        if use_terser:
            terser_available = ensure_terser_available()
            if not terser_available:
                logging.warning("无法安装或使用 terser，将跳过所有JS代码混淆")
        
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
            
        # 验证私钥文件（仅在crx格式时需要）
        if not use_zip:
            if not private_key_path or not os.path.exists(private_key_path):
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
        extension = 'zip' if use_zip else 'crx'
        output_file = os.path.join(output_dir, f"{extension_name}-{version}.{extension}")
        
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
        
        # 创建临时目录用于处理文件
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_files = []
            
            # 处理所有文件
            for rel_path, abs_path in files_to_pack:
                target_path = os.path.join(temp_dir, rel_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # 如果启用了terser且是JS文件，尝试混淆
                if use_terser and terser_available and rel_path.endswith('.js'):
                    if minify_js_file(abs_path, target_path):
                        processed_files.append((rel_path, target_path))
                        continue
                
                # 如果不需要混淆或混淆失败，直接复制
                import shutil
                shutil.copy2(abs_path, target_path)
                processed_files.append((rel_path, target_path))
            
            if use_zip:
                # 直接创建ZIP文件
                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for rel_path, abs_path in processed_files:
                        zf.write(abs_path, rel_path)
                logging.info(f"ZIP文件创建完成: {output_file}")
            else:
                # 创建临时ZIP文件
                zip_path = output_file + '.zip'
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for rel_path, abs_path in processed_files:
                        zf.write(abs_path, rel_path)
                logging.info("ZIP文件创建完成")
                
                # 读取ZIP内容
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
                
                # 写入CRX文件
                with open(output_file, 'wb') as f:
                    # CRX3格式头部
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
        if not use_zip and 'zip_path' in locals() and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                logging.debug("清理临时ZIP文件")
            except:
                pass 