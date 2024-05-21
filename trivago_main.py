import os

from trivago_task import TaTask
from trivago_login import TaLogin
from trivago_tool import TaConfig

# 获取当前脚本所在的目录
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
# 设置当前工作目录
os.chdir(current_dir)
print(current_dir)

def main():
    config = TaConfig().config
    driver = TaLogin().driver
    # 获取爬虫信息
    searchlist_path = config["searchlist"]["path"] + config["searchlist"]["name"]
    tasks = TaTask.get_tasks(searchlist_path)
    # 开始执行爬虫
    TaLogin().start(tasks)
    # 关闭浏览器
    driver.quit()


if __name__ == "__main__":  # ⼊⼝函数
    # 主逻辑
    main()
