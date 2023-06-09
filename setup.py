from cx_Freeze import setup, Executable

# 创建一个Executable对象
exec = Executable(
    script='trivago.py',  # 指定主要Python脚本文件的名称
    base=None,  # 可以指定GUI框架，如"Win32GUI"（用于创建GUI应用程序），或"Console"（用于创建控制台应用程序）
)

# 设置打包的参数
setup(
    name='trivago_scraping',
    version='1.1',
    description='Description of your app',
    executables=[exec]
)