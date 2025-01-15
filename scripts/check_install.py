import subprocess
import sys
import os
from scripts.venv_manager import ensure_venv, get_venv_python

def check_and_install_package():
    """检查并安装 crx-toolkit 包"""
    # 确保在虚拟环境中
    if not ensure_venv():
        print("Please restart the script to use the virtual environment")
        sys.exit(0)
    
    try:
        # 使用虚拟环境的 Python
        python_path = get_venv_python()
        # 检查包是否已安装
        subprocess.run([python_path, "-m", "pip", "show", "crx-toolkit"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Installing crx-toolkit...")
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        try:
            # 在虚拟环境中安装包
            subprocess.run([python_path, "-m", "pip", "install", "-e", root_dir], 
                         check=True)
            print("Successfully installed crx-toolkit")
        except subprocess.CalledProcessError as e:
            print(f"Error installing package: {e}")
            sys.exit(1)

if __name__ == "__main__":
    check_and_install_package() 