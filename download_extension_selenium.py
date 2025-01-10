from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import logging

logging.basicConfig(level=logging.INFO)

def download_with_selenium(extension_id):
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无界面模式
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": os.path.abspath("extension_files"),
        "download.prompt_for_download": False,
    })

    try:
        driver = webdriver.Chrome(options=chrome_options)
        url = f"https://chrome.google.com/webstore/detail/{extension_id}"
        driver.get(url)
        time.sleep(5)  # 等待页面加载
        
        # 找到下载按钮并点击
        download_button = driver.find_element_by_css_selector('.e-f-w')
        download_button.click()
        time.sleep(10)  # 等待下载完成
        
        driver.quit()
        return True
    except Exception as e:
        logging.error(f"Selenium下载失败: {e}")
        return False

# 使用方法
extension_id = "hniebljpgcogalllopnjokppmgbhaden"
download_with_selenium(extension_id) 