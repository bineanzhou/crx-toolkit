import os
import sys
import argparse
import logging
from typing import List, Optional
from .packer import pack_extension, setup_logging
from .downloader import download_crx

def clean_logs():
    """清理所有日志文件"""
    log_files = [
        'crx_pack.log',
        'crx_download.log',  # 下载相关的日志
        'crx_debug.log'      # 调试日志
    ]
    
    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                try:
                    # 先尝试关闭所有日志处理器
                    for handler in logging.root.handlers[:]:
                        handler.close()
                        logging.root.removeHandler(handler)
                except:
                    pass
                    
                # 然后删除文件
                os.remove(log_file)
                print(f"已清理历史日志文件: {log_file}")  # 使用 print 而不是 logging
        except Exception as e:
            print(f"清理日志文件 {log_file} 时发生错误: {str(e)}")  # 使用 print 而不是 logging

def main(args: Optional[List[str]] = None) -> int:
    """CLI 入口函数"""
    if args is None:
        args = sys.argv[1:]
        
    parser = argparse.ArgumentParser(description='Chrome扩展工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # pack 命令
    pack_parser = subparsers.add_parser('pack', help='打包扩展')
    pack_parser.add_argument('-s', '--source', required=True, help='扩展源目录路径')
    pack_parser.add_argument('-k', '--key', required=True, help='私钥文件路径')
    pack_parser.add_argument('-o', '--output', required=True, help='输出目录路径')
    pack_parser.add_argument('--no-force', action='store_true', help='不覆盖已存在的文件')
    pack_parser.add_argument('-v', '--verbose', action='store_true', help='启用详细日志')
    pack_parser.add_argument('--no-verify', action='store_true', help='跳过签名验证')
    pack_parser.add_argument('--use-terser', action='store_true', help='使用terser混淆JavaScript代码')
    
    # download 命令
    download_parser = subparsers.add_parser('download', help='下载扩展')
    download_parser.add_argument('--url', required=True, help='扩展下载链接')
    download_parser.add_argument('-o', '--output', required=True, help='输出目录路径')
    download_parser.add_argument('--no-force', action='store_true', help='不覆盖已存在的文件')
    download_parser.add_argument('-v', '--verbose', action='store_true', help='启用详细日志')
    download_parser.add_argument('--no-verify', action='store_true', help='跳过签名验证')
    
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
        
    try:
        # 根据命令设置日志文件名
        log_file = 'crx_pack.log' if parsed_args.command == 'pack' else 'crx_download.log'
        
        # 清理日志并设置日志配置
        clean_logs()
        setup_logging(verbose=parsed_args.verbose, log_file=log_file)
        
        if parsed_args.command == 'pack':
            pack_extension(
                source_dir=parsed_args.source,
                private_key_path=parsed_args.key,
                output_dir=parsed_args.output,
                force=not parsed_args.no_force,
                verbose=parsed_args.verbose,
                no_verify=parsed_args.no_verify,
                use_terser=parsed_args.use_terser
            )
        elif parsed_args.command == 'download':
            download_crx(
                url=parsed_args.url,
                output_dir=parsed_args.output,
                force=not parsed_args.no_force,
                verbose=parsed_args.verbose,
                no_verify=parsed_args.no_verify
            )
            
        return 0
        
    except Exception as e:
        logging.error(str(e))
        return 1

if __name__ == '__main__':
    sys.exit(main()) 