from typing import List
from datetime import datetime

from trivago_log import TaLog
from trivago_tool import TaConfig

import openpyxl as px
from openpyxl import Workbook
from openpyxl.styles import NamedStyle


class TaTask:
    cityname: str = None
    checkin: datetime = None
    checkout: datetime = None
    roomtype: str = None
    currency: str = None
    star: int = None
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
                self.checkin,
                self.checkout,
                self.roomtype,
                self.currency,
                self.star,
            ) = cell
            self.roomtype = TaTask.ROOM_TYPE_SINGLE
            self.state = TaTask.STATE_NORMAL

        except Exception as e:
            TaLog().error(f"{self.log_key}TaTask init error: {e}")
            TaLog().error(f"{self.log_key}{cell}")

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

    def check_roomtype(self, roomtype: str):
        if roomtype != self.ROOM_TYPE_SINGLE:
            raise ValueError("房间类型错误")

        return roomtype

    @staticmethod
    def output_create():
        config = TaConfig().config
        filename = datetime.now().strftime("%Y%m%d%H%M")
        output_dir = config["output"]["path"]
        output_file = f"{output_dir}/{filename}.xlsx"
        wb = Workbook()
        # 获取活动工作表
        ws = wb.active

        # 设置工作表标题
        ws.title = "Sheet1"

        if "date_style" not in wb.named_styles:
            date_style = NamedStyle(name="date_style", number_format="YYYY年MM月DD日")
            wb.add_named_style(date_style)

        # 将标题写入第一行
        titles = config["output"]["titles"]
        for col_num, title in enumerate(titles, start=1):
            ws.cell(row=1, column=col_num, value=title)
        wb.save(output_file)
        return output_file

    @staticmethod
    def output(file_path, outputs: list[dict]):
        # 取searchlist数据
        wb = px.load_workbook(file_path)
        ws = wb.active

        # 找到最后一行
        last_row = ws.max_row + 1

        config = TaConfig().config
        titles = config["output"]["titles"]
        titles_dict = {title: index + 1 for index, title in enumerate(titles)}

        for output in outputs:
            # 将新数据写入最后一行
            for _, title in enumerate(output, start=1):
                cell = ws.cell(
                    row=last_row,
                    column=titles_dict.get(title),
                    value=output.get(title, ""),
                )
                if type(cell.value) == datetime:
                    cell.style = "date_style"

            last_row += 1

        # 保存工作簿
        wb.save(file_path)

    def checkin_for_url(self):
        return self.checkin.strftime("%Y%m%d")

    def checkout_for_url(self):
        return self.checkout.strftime("%Y%m%d")

    def star_for_url(self):
        config = TaConfig().config
        stars = config["stars"]
        return stars[self.star]

    @staticmethod
    def price_for_output(price: str):
        price = price.replace(",", "")
        return f"US{price}"

    @staticmethod
    def count_task_states(tasks: List["TaTask"]) -> dict:
        state_counts = {
            TaTask.STATE_NORMAL: 0,
            TaTask.STATE_ERROR: 0,
            TaTask.STATE_OVER: 0,
        }

        for task in tasks:
            if task.state == TaTask.STATE_NORMAL:
                state_counts[TaTask.STATE_NORMAL] += 1
            elif task.state == TaTask.STATE_ERROR:
                state_counts[TaTask.STATE_ERROR] += 1
            elif task.state == TaTask.STATE_OVER:
                state_counts[TaTask.STATE_OVER] += 1

        TaLog().info(state_counts)


def test():
    # Exam  ple usage:
    task1 = TaTask()
    task1.state = TaTask.STATE_NORMAL

    task2 = TaTask()
    task2.state = TaTask.STATE_ERROR

    task3 = TaTask()
    task3.state = TaTask.STATE_OVER

    task4 = TaTask()
    task4.state = TaTask.STATE_NORMAL

    task_list = [task1, task2, task3, task4]
    TaTask.count_task_states(task_list)
