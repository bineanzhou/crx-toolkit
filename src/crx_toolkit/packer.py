import os
from typing import Optional
from .signer import sign_extension
from .utils.file_utils import ensure_dir

def pack_extension(
    source_dir: str,
    private_key_path: str,
    output_dir: str,
    extension_name: Optional[str] = None
) -> str:
    """
    Pack a Chrome extension directory into a CRX file
    
    Args:
        source_dir: Path to the extension source directory
        private_key_path: Path to the private key file
        output_dir: Output directory for the CRX file
        extension_name: Optional name for the output CRX file
        
    Returns:
        str: Path to the generated CRX file
    """
    # Ensure directories exist
    ensure_dir(output_dir)
    
    # Validate source directory
    if not os.path.isdir(source_dir):
        raise ValueError(f"Source directory not found: {source_dir}")
        
    # Read manifest.json to get extension info
    manifest_path = os.path.join(source_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        raise ValueError(f"manifest.json not found in {source_dir}")
    
    # Generate output filename
    if not extension_name:
        extension_name = os.path.basename(source_dir)
    crx_path = os.path.join(output_dir, f"{extension_name}.crx")
    
    # Sign the extension
    signed_data = sign_extension(source_dir, private_key_path)
    
    # Write CRX file
    with open(crx_path, 'wb') as f:
        f.write(signed_data)
        
    return crx_path 