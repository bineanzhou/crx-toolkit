import click
import logging
import json
from urllib.parse import urlparse, unquote
from .packer import pack_extension
from .downloader import download_crx
import os

@click.group()
def cli():
    """CRX 工具库命令行工具"""
    pass

@cli.command()
@click.option('--source', required=True, help='扩展源目录路径')
@click.option('--key', required=True, help='私钥文件路径')
@click.option('--output', default='output', help='输出目录路径')
@click.option('--force', is_flag=True, help='强制覆盖已存在的文件')
@click.option('--verbose', is_flag=True, help='启用详细输出')
@click.option('--no-verify', is_flag=True, help='跳过签名验证')
def pack(source, key, output, force, verbose, no_verify):
    """打包 Chrome 扩展为 CRX 文件"""
    try:
        result = pack_extension(
            source_dir=source,
            private_key_path=key,
            output_dir=output,
            force=force,
            verbose=verbose,
            no_verify=no_verify
        )
        click.echo(f"打包成功: {result}")
    except Exception as e:
        click.echo(f"打包失败: {str(e)}", err=True)
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