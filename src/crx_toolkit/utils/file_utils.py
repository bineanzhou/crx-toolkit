import os
import shutil

def ensure_dir(directory: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_dir(directory: str) -> None:
    """Clean a directory by removing and recreating it"""
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory) 