import time
import re

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
from selenium.webdriver.remote import webelement

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService


class TaLogin:
    _instance = None
    driver: wd = None
    current_task: TaTask = None

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
        self.current_task = task
        _config = TaConfig().config
        _driver = self.driver

        TaLog().info(f"{self.current_task.log_key}start query")
        TaLog().info(f"{self.current_task.log_key}{self.current_task}")

        if self.current_task.state is TaTask.STATE_NORMAL:
            self.goto_url()

        self.current_task.state = TaTask.STATE_OVER
        TaLog().info(f"{self.current_task.log_key}end query")

    def goto_url(self):
        _config = TaConfig().config
        _db = TaDB()

        search_key = self.current_task.cityname
        sql = _db.tables["city"][_db.SQL_TYPE_SEARCH]
        ret = _db.to_do(TaDB.SQL_TYPE_SEARCH, sql, (search_key,))

        template_obj = _config["home_page"]["template"]
        temp_url = template_obj["url"]
        temp_url += template_obj["param"]

        # 如果db中存在code
        if len(ret) == 0:
            self.get_code()
            ret = _db.to_do(TaDB.SQL_TYPE_SEARCH, sql, (search_key,))

        row = ret[0]
        replace_values = {
            "city_country": row[0],
            "code": row[1],
            "checkin": self.current_task.format_date(self.current_task.checkin),
            "checkout": self.current_task.format_date(self.current_task.checkout),
            "child_ages": "",
        }
        if self.current_task.roomtype == self.current_task.ROOM_TYPE_SINGLE:
            replace_values["rooms"] = "1"
            replace_values["adults"] = "2"
        url = make_url(temp_url, replace_values)
        self.current_task.url = url
        self.get_accommodation_list()

    def get_accommodation_list(self):
        _driver = TaLogin().driver

        TaLog().info(f"{self.current_task.log_key}{self.current_task.url}")
        _driver.get(self.current_task.url)

        wait = WebDriverWait(_driver, 10)
        # 找到指定的div元素
        selector = '//*[@data-testid="loading-animation-accommodations-counter"]'
        hotels_count = wait.until(
            EC.visibility_of_element_located((By.XPATH, selector))
        )
        TaLog().info(f"{self.current_task.log_key}{hotels_count.text}")

        selector = '//*[@data-testid="accommodation-list"]//*[@data-testid="accommodation-list-element"]'
        accommodation_list = _driver.find_elements(By.XPATH, selector)
        index = 0
        outputs = []
        for accommodation in accommodation_list:
            index += 1
            TaLog().info(f"{self.current_task.log_key}accommodation: {index}")
            output = get_accommodation_info(accommodation)
            outputs.append(output)

    def get_code(self):
        temp_url = self.default_url()
        _driver = self.driver
        # 调用函数生成完整的 URL
        _driver.get(temp_url)

        # 创建ActionChains对象
        actions = ActionChains(_driver)
        wait = WebDriverWait(_driver, 10)
        default_url = _driver.current_url

        # 找到指定的div元素
        selector = '//*[@role="combobox"]//*[@id="input-auto-complete"]'
        # 获取城市输入框
        destination_input = wait.until(
            EC.visibility_of_element_located((By.XPATH, selector))
        )
        try:
            selector = '//button[@data-testid="calendar-button-close"]'
            calendar_button_close = _driver.find_element(By.XPATH, selector)
            actions.move_to_element(calendar_button_close).click().perform()
        except:
            pass

        # 模拟鼠标移动到div元素并点击
        actions.move_to_element(destination_input).click().perform()

        # 执行键盘输入"Nagoya"
        destination_input.send_keys(self.current_task.cityname)

        # 点击第一个选项
        selector = '//*[@id="suggestion-list"]//*[@role="listbox"]//li[1]'
        first_button = wait.until(
            EC.visibility_of_element_located((By.XPATH, selector))
        )

        actions.move_to_element(first_button).click().perform()
        wait_time = 10
        time_count = 0
        current_url = default_url
        while time_count < wait_time and current_url == default_url:
            time_count += 1
            time.sleep(1)
            current_url = _driver.current_url

        if current_url == default_url:
            raise ValueError(f"url not change: {default_url}")

        TaLog().info(f"{self.current_task.log_key}current_url: {current_url}")

        # 正则表达式模式
        pattern = r"hotels-(.*)\?search=(\d+-\d+);"

        # 使用正则表达式查找匹配项
        match = re.search(pattern, current_url)

        if match:
            city_country = match.group(1)
            code = match.group(2)
            TaLog().info(f"city_country: {city_country}, code: {code}")
            db = TaDB()

            sql = db.tables["city"][db.SQL_TYPE_INSERT]
            db.to_do(
                db.SQL_TYPE_INSERT,
                sql,
                (self.current_task.cityname, city_country, code),
            )
        else:
            TaLog().error(
                f"{self.current_task.log_key}没有找到URL的code匹配项: {current_url}"
            )
            raise ValueError("没有找到URL的code匹配项")

    def default_url(self):
        _config = TaConfig().config
        template_obj = _config["home_page"]["template"]
        temp_url = template_obj["url"]
        temp_url += template_obj["param"]
        default_value = template_obj["default"]
        replace_values = {
            "city_country": default_value["city_country"],
            "code": default_value["code"],
            "checkin": self.current_task.format_date(self.current_task.checkin),
            "checkout": self.current_task.format_date(self.current_task.checkout),
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


def get_accommodation_info(accommodation: webelement):
    output = {}
    element = accommodation.find_element(
        By.XPATH,
        './/*[@data-testid="details-section"]//*[@data-testid="item-name"]//span',
    )
    output["Hotelname"] = element.text
    try:
        element = accommodation.find_element(
            By.XPATH, './/*[@data-testid="star-rating"]//meta'
        )
        output["Star"] = element.get_attribute("content")
    except:
        output["Star"] = ""

    try:
        element = accommodation.find_element(
            By.XPATH, './/*[@data-testid="recommended-price-partner"]'
        )
        output["Recommend booking"] = element.text
        element = accommodation.find_element(
            By.XPATH,
            './/*[@data-testid="clickout-area"]//*[@data-testid="recommended-price"]',
        )
        output["price"] = element.text
    except:
        output["Recommend booking"] = ""
        output["price"] = ""

    try:
        element = accommodation.find_element(
            By.XPATH, './/*[@data-testid="alternative-deal"]//*[@itemprop="name"]'
        )
        output["Other1 booking"] = element.text
        element = accommodation.find_element(
            By.XPATH, './/*[@data-testid="alternative-deal"]//*[@itemprop="price"]'
        )
        output["Other1 price"] = element.text
    except:
        output["Other1 booking"] = ""
        output["Other1 price"] = ""

    try:
        element = accommodation.find_element(
            By.XPATH, './/*[@data-testid="cheapest-price-label"]/span/span[3]'
        )
        output["lowest booking"] = element.text
        element = accommodation.find_element(
            By.XPATH, './/*[@data-testid="cheapest-price-label"]//*[@itemprop="price"]'
        )
        output["lowest price"] = element.text
    except:
        output["lowest booking"] = output["Recommend booking"]
        output["lowest price"] = output["price"]
    TaLog().info(output)
    return output


def test():
    # $x('//*[@data-testid="modal-container"]//button')[0] 关闭注册窗口
    # 示例模板 URL
    temp_url = "https://www.trivago.hk/en-HK/srl/hotels-cannes-france?search=105-1318;200-23033;dr-20240520-20240525;rc-1-2"

    _driver = TaLogin().driver

    _driver.get(temp_url)
    wait = WebDriverWait(_driver, 10)
    # 找到指定的div元素
    selector = '//*[@data-testid="loading-animation-accommodations-counter"]'
    hotels_count = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
    TaLog().info(hotels_count.text)

    _driver.quit()
