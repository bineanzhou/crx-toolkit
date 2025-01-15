import click
from .packer import pack_extension
from .downloader import download_crx
from .parser import parse_crx

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

@cli.command()
@click.option('--url', required=True, help='CRX file URL')
@click.option('--output', required=True, help='Output directory')
def download(url, output):
    """Download a CRX file from URL"""
    try:
        result = download_crx(url, output)
        click.echo(f"Successfully downloaded CRX file: {result}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--file', required=True, help='CRX file to parse')
def parse(file):
    """Parse and display CRX file information"""
    try:
        result = parse_crx(file)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli() 