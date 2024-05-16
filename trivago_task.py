import openpyxl as px

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
            _config =  TaConfig().config
            hk_hp = _config["home_page"]["hk"]
            self.url = hk_hp

        except Exception as e:
            TaLog().error(f"{self.log_key}TaTask init error: {e}")
            TaLog().error(f"{self.log_key}: {cell}")

    # print
    def __repr__(self):
        return str(self.__dict__)

    @classmethod
    def get_tasks(cls, file_path):
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
        if (
            self.cityname == None
            or self.checkin == None
            or self.checkout == None
        ):
            TaLog().error(f"{self.log_key}error data: {self}")
            return True
        return False
    
    def set_url(self):
        logger = TaLog().logger
        _config = TaConfig().config
        _driver = self.driver

        template_obj=_config["home_page"]["template"]
        url = template_obj["url"]
        param = template_obj["param"]
        default_value = template_obj["default"]

