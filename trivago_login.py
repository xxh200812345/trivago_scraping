import time

from trivago_log import TaLog
from trivago_task import TaTask
from trivago_tool import TaConfig
from trivago_db import TaDB

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as wd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService


class TaLogin:
    _instance = None
    driver: wd = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaLogin, cls).__new__(cls)
            cls._instance.driver = cls._instance.driver_init_chrome()
        return cls._instance

    def driver_init_chrome(self):
        TaLog().info("启动chrome浏览控制器")

        _config = TaConfig().config

        # 创建Chrome浏览器选项
        options = webdriver.ChromeOptions()

        # 添加浏览器参数
        for argument in _config["chrome_options"]["arguments"]:
            options.add_argument(argument)

        # 设置首选项
        if "prefs" in _config["chrome_options"]:
            options.add_experimental_option("prefs", _config["chrome_options"]["prefs"])

        # 启动Chrome浏览器
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

        # 打开一个新的空白标签页
        driver.execute_script("window.open('','_blank');")
        driver.switch_to.window(driver.window_handles[0])

        return driver

    def driver_init_edge(self):

        _config = TaConfig().config
        TaLog().info(f"启动edge浏览控制器")
        op = webdriver.EdgeOptions()
        

        # 添加浏览器参数
        for argument in _config["edge_options"]["arguments"]:
            op.add_argument(argument)

        # 设置首选项
        for key, value in _config["edge_options"]["prefs"].items():
            op.add_experimental_option(key, value)


        driver = webdriver.Edge(
            service=EdgeService(EdgeChromiumDriverManager().install()), options=op
        )
        driver.execute_script("window.open('','_blank');")
        driver.switch_to.window(driver.window_handles[0])
        return driver

    def has_element(self, byX, value):
        """
        检查元素是否存在
        """
        try:
            self.driver.find_element(byX, value)
            return True
        except:
            return False

    def is_bot_wait(self):
        """
        是否被判定为机器人,True 是机器人
        """
        element = self.driver.find_element(By.XPATH, "//div[@id='sec-overlay']")
        return element.is_displayed()

    def bot_check_wait(self, sleeptime=1):
        """
        如果被判定为机器人输入，等待
        """

        stime = 0
        time.sleep(sleeptime)
        if self.is_bot_wait():
            TaLog().info("反爬虫中...")
        # $x("")
        while self.is_bot_wait():
            time.sleep(1)
            # 超过31s依旧还在读取
            if stime > 31:
                self.driver.refresh()
                TaLog().info("超过31s依旧还在读取,刷新页面")
                stime = 0
                time.sleep(6)
            stime += 1
        if stime > 0:
            TaLog().info("反爬虫结束")

    def do_task(self, task: TaTask):
        """
        单独处理每一个task
        """

        _config = TaConfig().config
        _driver = self.driver

        TaLog().info(f"{task.log_key}start query")
        TaLog().info(f"{task.log_key}{task}")

        if task.state is TaTask.STATE_NORMAL:
            self.goto_url(task)

        task.state = TaTask.STATE_OVER
        TaLog().info(f"{task.log_key}end query")

    def goto_url(self, task: TaTask):
        _config = TaConfig().config
        _db = TaDB()
        _driver = self.driver

        search_key = task.cityname
        sql = _db.SQL_TYPE_SEARCH
        ret = _db.to_do(sql, (search_key,))

        template_obj = _config["home_page"]["template"]
        temp_url = template_obj["url"] + template_obj["param"]
        temp_url += template_obj["param"]

        # 如果db中存在code
        if len(ret) > 0:
            row = ret[0]
            replace_values = {
                "city": row[0],
                "country": row[1],
                "code": row[2],
                "checkin": task.checkin,
                "checkout": task.checkout,
                "child_ages": "",
            }
            if task.rooms == task.ROOM_TYPE_SINGLE:
                replace_values["rooms"] = "1"
                replace_values["adults"] = "2"
            url = make_url(temp_url, replace_values)
        else:
            # 没有code,通过构造url,查询search_key的code
            temp_url = self.get_code()
            # 存入db

        print(url)

    def get_code(self):
        temp_url = self.default_url()
        _driver = self.driver

    def default_url(self):
        _config = TaConfig().config
        template_obj = _config["home_page"]["template"]
        temp_url = template_obj["url"]
        temp_url += template_obj["param"]
        default_value = template_obj["default"]
        replace_values = {
            "city": default_value["city"],
            "country": default_value["country"],
            "code": default_value["code"],
            "checkin": self.checkin,
            "checkout": self.checkout,
            "rooms": "1",
            "adults": "2",
            "child_ages": "",
        }
        temp_url = make_url(temp_url, replace_values)
        return temp_url


def make_url(temp_url, data):
    # 使用字典的 items() 方法和循环来替换占位符
    for key, value in data.items():
        placeholder = f"{{{key}}}"
        temp_url = temp_url.replace(placeholder, str(value))
    return temp_url


def test():
    _driver = TaLogin().driver

    # 示例模板 URL
    temp_url = "https://www.trivago.hk/en-HK/srl/hotels-tokyo-japan?search=200-71462;dr-20240519-20240522;rc-1-2"

    # 调用函数生成完整的 URL
    _driver.get(temp_url)
    print(_driver.title)

    # 创建ActionChains对象
    actions = ActionChains(_driver)
    wait= WebDriverWait(_driver, 10)
    default_url = _driver.current_url

    # 找到指定的div元素
    selector = '//*[@role="combobox"]//*[@id="input-auto-complete"]'
    # 获取城市输入框
    destination_input = wait.until(
        EC.visibility_of_element_located((By.XPATH, selector))
    )
    try:
        selector = '//button[@dataitem="input-auto-complete"]'
        calendar_button_close =  _driver.find_element(By.XPATH, selector) 
        actions.move_to_element(calendar_button_close).click().perform()
    except:
        pass

    # 模拟鼠标移动到div元素并点击
    actions.move_to_element(destination_input).click().perform()

    # 执行键盘输入"Nagoya"
    destination_input.send_keys("Nagoya")
    

    # 点击第一个选项
    selector = '//*[@id="suggestion-list"]//*[@role="listbox"]//li[1]'
    first_button = wait.until(
        EC.visibility_of_element_located((By.XPATH, selector))
    )

    
    actions.move_to_element(first_button).click().perform()
    wait_time = 10
    time_count = 0
    current_url = default_url
    while(time_count < wait_time and current_url == default_url):
        time_count += 1
        time.sleep(1)
        current_url = _driver.current_url

    if current_url == default_url:
        raise ValueError(f"url not change: {default_url}")
    
    print(current_url)

    _driver.close()

test()
