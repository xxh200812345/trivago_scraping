<<<<<<< HEAD
# 使用方法
1. 需要chrome浏览器
1. chrome浏览器会自动打开，并自动打开trivago网页，进行搜索
   （爬虫工具，会根据searchlist.xlsx的条件，逐条搜索。最终搜完后会出现
    "Finished! Press Enter to close..." 提示）
1. 搜索结果会保存在output里面
1. 下载解压 res\exe.win-amd64-3.12.rar 压缩包，双击执行`trivago.exe`

# 文件
|  文件名   | 说明     |
|  ----  | ----  |
| run.bat   | 执行文件   |
| config/trivago_web.yml | 应用配置 |
| config/logging.yml | 日志配置 |
| res/searchlist.xlsx | 设定检索任务 |
| res/trivago.db | 设定检索任务 |
| trivago_main.py | 入口代码文件 |
| ts_env | 虚拟环境文件夹 |
| output | 输入结果文件夹 |
| log | 日志文件夹 |

# 生成trivago.exe
> python setup.py build