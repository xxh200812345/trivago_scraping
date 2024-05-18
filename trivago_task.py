import openpyxl as px
import re

from trivago_log import TaLog
from trivago_tool import TaConfig


class TaTask:
    cityname = None
    checkin = None
    checkout = None
    roomtype = None
    currency = None
    star = None
    log_key = None
    url = None
    ROOM_TYPE_SINGLE = "Single room"
    state = None

    STATE_NORMAL = "等待处理"
    STATE_ERROR = "数据错误"
    STATE_OVER = "处理结束"

    # init
    def __init__(self, cell: list, index: int):
        try:
            self.log_key = f"line[{index:06}] "
            (
                self.cityname,
                checkin,
                checkout,
                _,
                self.currency,
                star,
            ) = cell

            self.checkin = checkin.strftime("%Y-%m-%d")
            self.checkout = checkout.strftime("%Y-%m-%d")
            self.roomtype = TaTask.ROOM_TYPE_SINGLE
            self.star = self.check_star(star)

            self.state = TaTask.STATE_NORMAL

        except Exception as e:
            TaLog().error(f"{self.log_key}TaTask init error: {e}")
            TaLog().error(f"{self.log_key}: {cell}")

            self.state = TaTask.STATE_ERROR


    # print
    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def get_tasks(file_path):
        # 取searchlist数据
        searchlist_exl = px.load_workbook(file_path)
        ws = searchlist_exl.active

        tasks = []
        # Print the row data
        for index, row in enumerate(ws.iter_rows(min_row=2)):
            row_data = []
            for cell in row:
                row_data.append(cell.value)
            _task = TaTask(row_data, (index + 2))
            tasks.append(_task)
        return tasks

    def is_error_data(self):
        if self.cityname == None or self.checkin == None or self.checkout == None:
            TaLog().error(f"{self.log_key}error data: {self}")
            return True
        return False

    def format_date(self, datestr: str):
        # 正则表达式模式，用于匹配日期格式 YYYY-MM-DD
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        # 使用 match 函数验证日期格式
        match = re.match(date_pattern, datestr)
        if match:
            datestr = datestr.replace("-", "")
        else:
            TaLog().error(f"{self.log_key}日期格式错误")
            datestr = ""

        return datestr

    def check_roomtype(self, roomtype: str):
        if roomtype != self.ROOM_TYPE_SINGLE:
            raise ValueError("房间类型错误")

        return roomtype

    def check_star(self, star: int):
        if star not in [3, 4, 5]:
            raise ValueError("酒店星级设定错误")
        star = str(star)
        return star

def test():
    searchlist = TaConfig().config["searchlist"]
    tasks = TaTask.get_tasks(searchlist["path"] + searchlist["name"])
    for task in tasks:
        print(task)
