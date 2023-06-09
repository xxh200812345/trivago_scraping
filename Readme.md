# 使用方法1
1. 如果没有安装python，请先安装python
1. 安装如果完成可以用 python -V 查看版本。例如：Python 3.10.9
1. 双击执行`run.bat`
1. 自动下载chrome
1. chrome浏览器会自动打开，并自动打开trivago网页，进行搜索
   （爬虫工具，会根据searchlist.xlsx的条件，逐条搜索。最终搜完后会出现
    "Finished! Press Enter to close..." 提示）
1. 搜索结果会保存在output里面。

# 使用方法2
1. 下载解压 res\exe.win-amd64-3.10.rar 压缩包，双击执行`trivago.exe`

# 文件
|  文件名   | 说明     |
|  ----  | ----  |
| run.bat   | 执行文件   |
| logging.yml | 日志配置 |
| searchlist.xlsx | 设定检索任务 |
| trivago.py | 主要代码文件 |
| trivago_venv | 虚拟环境文件夹 |
| output | 输入结果文件夹 |
| info.log | 日志 |

# 环境搭建：

关于执行的学习录像也有提供，请看

# 生成trivago.exe

    python setup.py build