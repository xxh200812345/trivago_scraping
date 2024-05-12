import openpyxl as px

from trivago_log import TaLog
from trivago_login import TaLogin
from trivago_tool import TaConfig


class TaTask:
    cityname = None
    checkin = None
    checkout = None
    roomtype = None
    currency = None
    star = None


    # init
    def __init__(self, cell: list, index: int):
        try:
            self.cityname, self.checkin, self.checkout, \
                self.roomtype, self.currency, self.star = cell
        except Exception as e:
            TaLog().error(f"TaTask init error: {e}")
            TaLog().error(f"error line[{index}]: {cell}")

    # print
    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def get(cls, file_path):
        # 取searchlist数据
        searchlist_exl = px.load_workbook(file_path)
        ws = searchlist_exl.active

        tasks = []
        # Print the row data
        for index, row in enumerate(ws.iter_rows(min_row=2)):
            row_data = []
            for cell in row:
                row_data.append(cell.value)
            _task = TaTask(row_data, (index+2))
            tasks.append(_task)
        return tasks


def logging_init():
    pass


def start(tasks):
    # 开始执行爬虫
    pass


def main():
    _config = TaConfig().config
    _driver = TaLogin().driver
    # 获取爬虫信息
    searchlist_path = _config['searchlist']['path'] + \
        _config['searchlist']['name']
    tasks = TaTask.get(searchlist_path)
    # 开始执行爬虫
    # start(tasks)
    # 关闭浏览器
    _driver.close()


if __name__ == "__main__":  # ⼊⼝函数
    # 初始化
    logging_init()
    # 主逻辑
    main()
