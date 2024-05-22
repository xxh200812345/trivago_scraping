# 使用方法
1. 需要chrome浏览器
2. 下载解压 `res\exe.win-amd64-3.12.rar` 压缩包，双击执行`trivago.exe`
3. chrome浏览器会自动打开，并自动打开trivago网页，进行搜索
   （爬虫工具，会根据`res/searchlist.xlsx`的条件，逐条搜索。
4. `log/info.log` 里可以查看搜索过程。
5. 目前在处理第几行检索可以参考`处理中log`的`line[000005]`，编号对应检索条件的行号。搜索结束参考`处理结果log`。
6. 搜索结果会保存在`output/{日期时分}.xlsx`里面


# 参考
## 处理结果log
> ：2024-05-23 01:39:59,550 - trivago_log.py -root -INFO - {'等待处理': 0, '数据错误': 0, '处理结束': 4}
## 处理中log
> 2024-05-23 01:39:48,176 - trivago_log.py -root -INFO - line[000005] 开始下载数据,page(2/2)
## 文件
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


## 生成trivago_main.exe
> python setup.py build

## QA
1. 删除输出结果中的other3（空白列）
2. 记录所有真实检索数据（比如无星级的情况）
3. 输出结果增加房屋类型（Hotel \ ...）
4. 货币保留网页原始结果
5. 货币锁定美元
6. 房间类型锁定Single room
7. 酒店只检索3，4，5星级
