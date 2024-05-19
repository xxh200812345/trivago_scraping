from trivago_task import TaTask
from trivago_log import TaLog
from trivago_login import TaLogin
from trivago_tool import TaConfig

def logging_init():
    pass


def main():
    _config = TaConfig().config
    _driver = TaLogin().driver
    # 获取爬虫信息
    searchlist_path = _config["searchlist"]["path"] + _config["searchlist"]["name"]
    tasks = TaTask.get_tasks(searchlist_path)
    # 开始执行爬虫
    TaLogin().start(tasks)
    # 关闭浏览器
    _driver.quit()

if __name__ == "__main__":  # ⼊⼝函数
    # 初始化
    logging_init()
    # 主逻辑
    main()
