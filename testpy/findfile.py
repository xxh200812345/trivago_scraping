import tkinter as tk
from tkinter import filedialog
import configparser
import os

os.chdir(os.path.abspath(os.path.dirname(__file__)))

config=None

def config_init():
    # 创建一个ConfigParser对象
    config = configparser.ConfigParser()
    config.read(r"H:\vswork\trivago_scraping\config.ini", encoding="utf-8")

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()

    key = config.get('Section', 'file_path')
    print(f"key: {key}")

        # 弹出文件选择框
    file_path = filedialog.askopenfilename(title="Select Excel File for Query Conditions",
                                           filetypes=[("Excel文件", "*.xlsx;*.xls")])
    
    # 更新配置文件中的路径
    config.set('Section', 'file_path', file_path)

    # 写入配置文件
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    print("文件路径已保存到config.ini文件中。")

config_init()
open_file_dialog()