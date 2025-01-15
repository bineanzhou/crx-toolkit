from typing import Dict, Any
import json
import zipfile

def parse_crx(crx_path: str) -> Dict[str, Any]:
    """
    Parse a CRX file and extract its information
    
    Args:
        crx_path: Path to the CRX file
        
    Returns:
        dict: Information about the CRX file
    """
    result = {
        'format_version': None,
        'manifest': None,
        'files': [],
        'size': 0
    }
    
    try:
        with zipfile.ZipFile(crx_path, 'r') as crx:
            # Read manifest.json
            try:
                manifest = json.loads(crx.read('manifest.json'))
                result['manifest'] = manifest
            except:
                result['manifest'] = None
                
            # List all files
            result['files'] = crx.namelist()
            
            # Get total size
            result['size'] = sum(info.file_size for info in crx.filelist)
            
    except Exception as e:
        raise ValueError(f"Failed to parse CRX file: {str(e)}")
        
    return result 