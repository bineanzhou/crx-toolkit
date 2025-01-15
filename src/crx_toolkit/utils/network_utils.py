import requests
from typing import Optional

def download_file(url: str, output_path: str, timeout: Optional[int] = 30) -> None:
    """
    Download a file from URL to the specified path
    
    Args:
        url: Source URL
        output_path: Where to save the file
        timeout: Request timeout in seconds
    """
    response = requests.get(url, timeout=timeout, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk) 