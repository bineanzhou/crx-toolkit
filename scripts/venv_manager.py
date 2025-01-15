import os
import sys
import subprocess
import platform
from pathlib import Path

def get_venv_path():
    """获取虚拟环境路径"""
    root_dir = Path(__file__).parent.parent
    return root_dir / '.venv'

def is_venv_activated():
    """检查是否已在虚拟环境中"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def create_venv():
    """创建虚拟环境"""
    venv_path = get_venv_path()
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print(f"Virtual environment created at {venv_path}")
    return venv_path

def get_venv_python():
    """获取虚拟环境中的 Python 解释器路径"""
    venv_path = get_venv_path()
    if platform.system() == "Windows":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    return str(python_path)

def install_package():
    """在虚拟环境中安装包"""
    root_dir = Path(__file__).parent.parent
    python_path = get_venv_python()
    
    print("Installing package in virtual environment...")
    subprocess.run([python_path, "-m", "pip", "install", "-e", str(root_dir)], check=True)
    print("Package installed successfully")

def ensure_venv():
    """确保在虚拟环境中运行"""
    if not is_venv_activated():
        venv_path = create_venv()
        install_package()
        return False
    return True

if __name__ == "__main__":
    ensure_venv() 