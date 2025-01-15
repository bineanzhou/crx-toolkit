import click
import json
from urllib.parse import urlparse, unquote
from .packer import pack_extension
from .downloader import download_crx
from .parser import parse_crx
import os

@click.group()
def cli():
    """CRX Toolkit - Chrome Extension Package Manager"""
    pass

@cli.command()
@click.option('--source', required=True, help='Extension source directory')
@click.option('--key', required=True, help='Private key file path')
@click.option('--output', required=True, help='Output directory')
def pack(source, key, output):
    """Pack a Chrome extension into CRX format"""
    try:
        result = pack_extension(source, key, output)
        click.echo(f"Successfully created CRX file: {result}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.option('--url', required=True, help='CRX file URL')
@click.option('--output', required=True, help='Output directory')
@click.option('--proxy', help='Proxy server (e.g., http://127.0.0.1:7890)')
def download(url, output, proxy):
    """Download a CRX file from URL"""
    try:
        # URL 解码和清理
        decoded_url = unquote(url).strip('"\'')
        
        # 创建输出目录
        os.makedirs(output, exist_ok=True)
        
        result = download_crx(decoded_url, output, proxy=proxy)
        click.echo(f"Successfully downloaded CRX file: {result}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.option('--file', required=True, help='CRX file to parse')
def parse(file):
    """Parse and display CRX file information"""
    try:
        result = parse_crx(file)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli() 