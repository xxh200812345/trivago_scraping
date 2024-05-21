from cx_Freeze import setup, Executable

# 创建一个Executable对象
exec = Executable(
    script='trivago_main.py',  # 指定主要Python脚本文件的名称
    base="Win32GUI",  # 可以指定GUI框架，如"Win32GUI"（用于创建GUI应用程序），或"Console"（用于创建控制台应用程序）
)

build_exe_options = {
    "packages": ["os", "sys"],
    "excludes": ["tkinter"],
    "include_files": [("config/","config/"),("res/","res/")]  # Include the data directory
}

# 设置打包的参数
setup(
    name='trivago_scraping',
    version='2.1',
    description='Description of your app',
    options = {"build_exe": build_exe_options},
    executables=[exec]
)