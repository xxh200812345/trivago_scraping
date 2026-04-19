# Trivago 数据采集自动化工具

这是一个基于 Selenium 的自动化爬虫工具，专门用于根据预设条件从 Trivago 平台检索并采集酒店价格、评价等信息。

## 🚀 使用方法

1. **环境准备**：确保本地已安装 **Google Chrome** 浏览器。
2. **启动程序**：
   - 下载并解压 `exe.win-amd64-3.12.zip`。
   - 双击执行目录下的 `trivago.exe`。
3. **自动运行**：
   - 程序启动后会自动唤起 Chrome 浏览器并访问 Trivago。
   - 脚本将读取 `res/searchlist.xlsx` 中的配置，执行逐条检索。
4. **状态监控**：
   - **实时日志**：检查 `log/info.log` 了解详细搜索过程。
   - **进度参考**：在日志中搜索关键词 `line[xxxxxx]`（如 `line[000005]`），该编号对应 `searchlist.xlsx` 中的行号。
   - **监视器**：启动程序后，可双击运行 `res/watch.bat` 进行实时状态追踪。
5. **获取结果**：
   - 任务完成后，结果将保存在 `output/{日期时分}.xlsx` 中。

### 高级配置：真实浏览器接管模式
在 config/trivago_web.yml 中，你可以通过 use_actual_browser 切换运行模式：

1. 接管模式 (Recommended)
   配置：use_actual_browser: true

   原理：Python 会自动启动一个真实的 Chrome 进程，并将其数据存储在项目根目录的 chrome_profile 文件夹中。

2. 标准模式

   配置：use_actual_browser: false

   原理：使用传统的 Selenium 驱动模式，每次启动都是一个纯净的、无痕的“沙盒”浏览器。
---

## 📂 项目结构说明

| 文件/文件夹 | 说明 |
| :--- | :--- |
| **run.bat** | 程序快速启动脚本 |
| **config/trivago_web.yml** | **核心配置**：包含浏览器开关、爬虫逻辑及选择器设定 |
| **config/logging.yml** | 日志输出格式及级别配置 |
| **res/searchlist.xlsx** | **任务清单**：在此定义需要检索的城市、日期、人数等条件 |
| **res/trivago.db** | 本地缓存数据库（用于存储城市代码等映射数据） |
| **trivago_main.py** | 程序入口源代码 |
| **.venv/** | Python 虚拟环境运行库 |
| **output/** | 搜索结果导出文件夹（Excel 格式） |
| **log/** | 系统运行日志文件夹 |

---

## 📊 日志参考范例

### 处理中进度 (Progress)
> `2024-05-23 01:39:48,176 - INFO - line[000005] 开始下载数据, page(2/2)`
*表示当前正在处理 Excel 第 5 行的任务，且处于第 2 页数据采集阶段。*

### 任务结算 (Summary)
> `2024-05-23 01:39:59,550 - INFO - {'等待处理': 0, '数据错误': 0, '处理结束': 4}`
*任务完成后会输出统计摘要。*

---

## 🛠 开发与构建
如需修改代码后重新生成 `.exe` 可执行文件，请在终端执行：
```bash
python setup.py build