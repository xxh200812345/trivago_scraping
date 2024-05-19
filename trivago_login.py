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
    current_max_page = 1
    current_page = 1
    loading_wait_time = 1
    output_path = ""

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

    def set_star(self):
        _driver = self.driver

        # 获取当前星级 'Remove\n3,4 Stars'

        selector = '//*[contains(@class,"HorizontalScrollRow_wrapper__MUuNp")]'
        try:
            star_info_element = _driver.find_element(By.XPATH, selector)
            star_info = star_info_element.text
        except:
            star_info = ""

        # 非当前星级的情况，设置成当前星级
        star = str(self.current_task.star)
        if not f"{star} Stars" in star_info:
            actions = ActionChains(_driver)
            # click filters
            selector = '//button[@name="more_filters"]'
            filters_btn = wait_find_element_xpath(selector)
            actions.move_to_element(filters_btn).click().perform()

            # reset
            selector = '//button[@data-testid="filters-popover-reset-button"]'
            reset_btn = _driver.find_element(By.XPATH, selector)
            if not reset_btn.get_attribute("disabled"):
                actions.move_to_element(reset_btn).click().perform()

            # set star
            selector = f'//button[@data-testid="{star}-star-hotels-filter"]'
            star_btn = _driver.find_element(By.XPATH, selector)
            actions.move_to_element(star_btn).click().perform()

            # apply
            selector = '//button[@data-testid="filters-popover-apply-button"]'
            apply_btn = _driver.find_element(By.XPATH, selector)
            actions.move_to_element(apply_btn).click().perform()

    def set_currency(self):
        _driver = self.driver
        _config = TaConfig().config

        # 获取当前货币符号
        selector = '//header//*[@data-testid="header-localization-menu"]/span[2]/span'
        current_sign_element = wait_find_element_xpath(selector)
        current_sign = current_sign_element.text
        TaLog().info(f"{self.current_task.log_key}localization: {current_sign}")
        current_sign = current_sign.split("·")[1]
        current_sign = current_sign.strip()

        # 用货币符号找到对应的货币缩写
        current_name = ""
        currency_list = _config["currency_list"]
        for currency in currency_list:
            current_name = currency["name"]
            sign = currency["sign"]
            if sign == current_sign:
                break

        # 如果货币和搜索数据不一致，则改成一致
        actions = ActionChains(_driver)
        if current_name != self.current_task.currency:
            TaLog().info(
                f"{self.current_task.log_key}currency: {current_sign} -> {self.current_task.currency}"
            )
            selector = '//header//*[@data-testid="header-localization-menu"]'
            header_localization_menu_btn = wait_find_element_xpath(selector)
            actions.move_to_element(header_localization_menu_btn).click().perform()

            selector = f'//*[@id="currency-select"]'
            currency_select = wait_find_element_xpath(selector)
            actions.move_to_element(currency_select).click().perform()

            # 设置成task中的货币
            select = Select(currency_select)
            select.select_by_value(self.current_task.currency)

            selector = '//dialog//button[@type="submit"]'
            dialog_apply_btn = wait_find_element_xpath(selector)
            actions.move_to_element(dialog_apply_btn).click().perform()

    def do_task(self, task: TaTask):
        """
        单独处理每一个task
        """
        _config = TaConfig().config

        self.loading_wait_time = _config["loading_wait_time"]
        self.current_task = task
        TaLog().info(f"{self.current_task.log_key}start query")
        TaLog().info(f"{self.current_task.log_key}{self.current_task}")

        if self.current_task.state is TaTask.STATE_NORMAL:
            self.goto_url()
            self.current_page = 1
            self.get_accommodation_list()

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

    def get_accommodation_list(self):
        """
        初始化指定条件下第一页下载列表
        """
        _driver = TaLogin().driver

        TaLog().info(f"{self.current_task.log_key}初始化下载环境")
        TaLog().info(f"{self.current_task.log_key}{self.current_task.url}")
        _driver.get(self.current_task.url)

        # accommodations-counter
        selector = '//*[@data-testid="loading-animation-accommodations-counter"]'
        hotels_count = wait_find_element_xpath(selector)
        TaLog().info(f"{self.current_task.log_key}{hotels_count.text}")

        # 关闭日期选择
        close_calendar()

        # 设置货币
        self.set_currency()
        # 设置星级
        self.set_star()

        # 广告商列表
        selector = '//*[@data-testid="accommodation-list"]'
        wait_find_element_xpath(selector)

        # 最大页数
        try:
            if self.current_page == 1:
                selector = '//*[@data-testid="pagination"]/li'
                selector = '//*[@data-testid="pagination"]'
                pagination_ol = _driver.find_element(By.XPATH, selector)
                pages = pagination_ol.text.strip().split("\n")

                self.current_max_page = 1
                if len(pages) > 1:
                    self.current_max_page = int(pages[-1])
        except:
            self.current_max_page = 1

        for i in range(self.current_page, self.current_max_page + 1):
            self.current_page = i
            self.accommodation_list_loop()

    def accommodation_list_loop(self):
        """
        获取指定页面的全部广告商数据
        """
        _driver = TaLogin().driver

        url = self.current_task.url
        if self.current_max_page != 1 and self.current_page <= self.current_max_page:
            url += f";pa-{str(self.current_page)}"
        page_info = f"page({str(self.current_page)}/{str(self.current_max_page)})"
        TaLog().info(f"{self.current_task.log_key}开始下载数据,{page_info}")
        TaLog().info(f"{self.current_task.log_key}{url}")

        time.sleep(self.loading_wait_time)
        if self.current_page != 1:
            _driver.get(url)

        # 广告商列表
        selector = '//*[@data-testid="accommodation-list"]'
        wait_find_element_xpath(selector)
        

        selector = '//*[@data-testid="accommodation-list"]//*[@data-testid="accommodation-list-element"]'
        accommodation_list = _driver.find_elements(By.XPATH,selector)

        index = 0
        outputs = []
        for accommodation in accommodation_list:
            index += 1
            output = get_accommodation_info(accommodation)
            output["City"] = self.current_task.cityname
            output["Checkin"] = self.current_task.checkin
            output["Checkout"] = self.current_task.checkout
            output["Currency"] = self.current_task.currency

            TaLog().info(f"{self.current_task.log_key}{index}: {output}")
            outputs.append(output)
        self.current_task.output(self.output_path, outputs)

    def get_code(self):
        temp_url = self.default_url()
        _driver = self.driver
        # 调用函数生成完整的 URL
        _driver.get(temp_url)

        # 创建ActionChains对象
        actions = ActionChains(_driver)
        default_url = _driver.current_url

        # 找到指定的div元素
        selector = '//*[@role="combobox"]//*[@id="input-auto-complete"]'
        # 获取城市输入框
        destination_input = wait_find_element_xpath(selector)

        close_calendar()

        # 模拟鼠标移动到div元素并点击
        actions.move_to_element(destination_input).click().perform()

        # 执行键盘输入"Nagoya"
        destination_input.send_keys(self.current_task.cityname)

        # 点击第一个选项
        selector = '//*[@id="suggestion-list"]//*[@role="listbox"]//li[1]'
        first_button = wait_find_element_xpath(selector)

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

    def start(self, tasks: list[TaTask]):
        TaLog().info(f"start query")

        self.output_path =  TaTask.output_create()

        # 开始执行爬虫
        for task in tasks:
            TaLogin().do_task(task)

def close_calendar():
    _driver = TaLogin().driver
    actions = ActionChains(_driver)
    try:
        selector = '//button[@data-testid="calendar-button-close"]'
        calendar_button_close = _driver.find_element(By.XPATH, selector)
        actions.move_to_element(calendar_button_close).click().perform()
    except:
        pass


def wait_find_element_xpath(selector, waittime=10):
    _driver = TaLogin().driver
    wait = WebDriverWait(_driver, waittime)
    # 找到指定的div元素
    element = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
    return element


def make_url(temp_url: str, data: dict):
    # 使用字典的 items() 方法和循环来替换占位符
    for key, value in data.items():
        placeholder = f"{{{key}}}"
        temp_url = temp_url.replace(placeholder, str(value))
    return temp_url


def get_accommodation_info(accommodation: webelement.WebElement):
    output = {}

    _config = TaConfig().config
    selectors = _config['selectors']

    for output_name, selector in selectors.items():
        try:
            element = accommodation.find_element(By.XPATH, selector)
            if output_name == "Star":
                output[output_name] = element.get_attribute("content")
            else:
                output[output_name] = element.text
        except:
            output[output_name] = ""

    if not output["lowest booking"]:
        output["lowest booking"] = output["Recommend booking"]
    if not output["lowest price"]:
        output["lowest price"] = output["price"]

    return output


def test():
    # $x('//*[@data-testid="modal-container"]//button')[0] 关闭注册窗口
    # 示例模板 URL
    temp_url = "https://www.trivago.hk/en-HK/srl/hotels-tokyo-japan?search=200-71462;dr-20240617-20240618;rc-1-2-4-6"

    _driver = TaLogin().driver

    _driver.get(temp_url)

    actions = ActionChains(_driver)

    # click filters
    selector = '//button[@name="more_filters"]'
    filters_btn = wait_find_element_xpath(selector)

    close_calendar()

    selector = '//*[@data-testid="pagination"]'
    pagination_ol = _driver.find_element(By.XPATH, selector)
    pages = pagination_ol.text.strip().split("\n")
    print(pages)

    _driver.quit()
