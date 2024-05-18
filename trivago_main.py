from trivago_task import TaTask
from trivago_log import TaLog
from trivago_login import TaLogin
from trivago_tool import TaConfig

def logging_init():
    pass


def start(tasks):
    TaLog().info(f"start query")
    # 开始执行爬虫
    for task in tasks:
        TaLogin().do_task(task)


def main():
    _config = TaConfig().config
    _driver = TaLogin().driver
    # 获取爬虫信息
    searchlist_path = _config["searchlist"]["path"] + _config["searchlist"]["name"]
    tasks = TaTask.get_tasks(searchlist_path)
    # 开始执行爬虫
    start(tasks)
    # 关闭浏览器
    _driver.quit()

if __name__ == "__main__":  # ⼊⼝函数
    # 初始化
    logging_init()
    # 主逻辑
    main()
