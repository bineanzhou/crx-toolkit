#!/bin/bash

# 设置日志文件
LOG_FILE="extension_download.log"
EXTENSION_URL="$1"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到 Python3${NC}"
        exit 1
    fi
}

# 检查必要的Python包
check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    python3 -c "import requests" 2>/dev/null || {
        echo -e "${YELLOW}安装 requests...${NC}"
        pip3 install requests
    }
    python3 -c "import selenium" 2>/dev/null || {
        echo -e "${YELLOW}安装 selenium...${NC}"
        pip3 install selenium
    }
}

# 清理旧文件
cleanup() {
    echo -e "${YELLOW}清理旧文件...${NC}"
    rm -f extension.crx extension.zip
    rm -rf extension_files/* 2>/dev/null
}

# 主下载函数
download_extension() {
    local url="$1"
    echo -e "${YELLOW}开始下载扩展: ${url}${NC}"
    
    # 1. 尝试直接下载
    echo -e "${YELLOW}方法1: 直接下载...${NC}"
    if python3 download_extension.py "$url"; then
        if [ -d "extension_files" ] && [ "$(ls -A extension_files)" ]; then
            echo -e "${GREEN}直接下载成功！${NC}"
            return 0
        fi
    fi
    
    # 2. 尝试使用Selenium
    echo -e "${YELLOW}方法2: 使用Selenium下载...${NC}"
    if python3 download_extension_selenium.py "$url"; then
        if [ -d "extension_files" ] && [ "$(ls -A extension_files)" ]; then
            echo -e "${GREEN}Selenium下载成功！${NC}"
            return 0
        fi
    fi
    
    # 3. 尝试从本地提取
    echo -e "${YELLOW}方法3: 从本地Chrome提取...${NC}"
    if python3 extract_local_extension.py "$url"; then
        if [ -d "extension_files" ] && [ "$(ls -A extension_files)" ]; then
            echo -e "${GREEN}本地提取成功！${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}所有下载方法都失败${NC}"
    return 1
}

# 分析扩展
analyze_extension() {
    echo -e "${YELLOW}开始分析扩展...${NC}"
    if python3 analyze_apis.py; then
        echo -e "${GREEN}分析完成！${NC}"
        return 0
    else
        echo -e "${RED}分析失败${NC}"
        return 1
    fi
}

# 主函数
main() {
    # 检查参数
    if [ -z "$EXTENSION_URL" ]; then
        echo -e "${RED}错误: 请提供扩展URL${NC}"
        echo "用法: $0 <扩展URL>"
        exit 1
    fi
    
    # 检查环境
    check_python
    check_dependencies
    
    # 清理旧文件
    cleanup
    
    # 下载扩展
    if download_extension "$EXTENSION_URL"; then
        # 分析扩展
        analyze_extension
    else
        echo -e "${RED}下载失败，退出${NC}"
        exit 1
    fi
}

# 执行主函数
main 2>&1 | tee -a "$LOG_FILE" 