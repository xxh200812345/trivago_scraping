import time
import re

from trivago_log import TaLog
from trivago_task import TaTask
from trivago_tool import TaConfig
from trivago_db import TaDB

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver as wd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote import webelement

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


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

        config = TaConfig().config

        # 创建Chrome浏览器选项
        options = webdriver.ChromeOptions()

        # 添加浏览器参数
        for argument in config["chrome_options"]["arguments"]:
            options.add_argument(argument)

        # 设置首选项
        if "prefs" in config["chrome_options"]:
            options.add_experimental_option("prefs", config["chrome_options"]["prefs"])

        # 启动Chrome浏览器
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

        # 打开一个新的空白标签页
        driver.execute_script("window.open('','_blank');")
        driver.switch_to.window(driver.window_handles[0])

        return driver

    def set_currency(self):
        driver = self.driver
        config = TaConfig().config

        # 获取当前货币符号
        selector = '//header//*[@data-testid="header-localization-menu"]/span[2]/span'
        localization_menu_element = wait_find_element_xpath(selector)
        localization_menu = localization_menu_element.text
        TaLog().info(
            f"{self.current_task.log_key}localization-menu: {localization_menu}"
        )

        # 用货币符号找到对应的货币缩写
        currency_dict = config["currency_dict"]
        current_sign = currency_dict[self.current_task.currency]



        # 如果货币和搜索数据不一致，则改成一致
        actions = ActionChains(driver)
        if current_sign not in localization_menu[-1]:
            TaLog().info(
                f"{self.current_task.log_key}currency:  -> {self.current_task.currency}"
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
        config = TaConfig().config

        self.loading_wait_time = config["loading_wait_time"]
        self.current_task = task
        TaLog().info(f"{self.current_task.log_key}start query")
        TaLog().info(f"{self.current_task.log_key}{self.current_task}")

        if self.current_task.state is TaTask.STATE_NORMAL:
            self.goto_url()

            if self.current_task.state == TaTask.STATE_ERROR:
                return

            self.current_page = 1
            self.get_accommodation_list()

        self.current_task.state = TaTask.STATE_OVER
        TaLog().info(f"{self.current_task.log_key}end query")

    def goto_url(self):
        config = TaConfig().config
        _db = TaDB()

        search_key = self.current_task.cityname
        sql = _db.tables["city"][_db.SQL_TYPE_SEARCH]
        ret = _db.to_do(TaDB.SQL_TYPE_SEARCH, sql, (search_key,))

        template_obj = config["home_page"]["template"]
        temp_url = template_obj["url"]
        temp_url += template_obj["param"]

        # 如果db中存在code
        if len(ret) == 0:
            self.get_code()

            if self.current_task.state == TaTask.STATE_ERROR:
                return
            ret = _db.to_do(TaDB.SQL_TYPE_SEARCH, sql, (search_key,))

        row = ret[0]
        replace_values = {
            "city_country": row[0],
            "code": row[1],
            "star": self.current_task.star_for_url(),
            "checkin": self.current_task.checkin_for_url(),
            "checkout": self.current_task.checkout_for_url(),
            "child_ages": "",
        }
        if self.current_task.roomtype == self.current_task.ROOM_TYPE_SINGLE:
            replace_values["rooms"] = "1"
            replace_values["adults"] = "2"
        url = make_url(temp_url, replace_values)
        self.current_task.url = url

    def open_url(self, url):
        driver = TaLogin().driver
        driver.get(url)

        # accommodations-counter
        selector = '//*[@data-testid="loading-animation-accommodations-counter"]'
        hotels_count = wait_find_element_xpath(selector)
        TaLog().info(f"{self.current_task.log_key}{hotels_count.text}")

        # 关闭日期选择
        close_calendar()

        # 设置货币
        self.set_currency()

    def get_accommodation_list(self):
        """
        初始化指定条件下第一页下载列表
        """
        driver = TaLogin().driver

        TaLog().info(f"{self.current_task.log_key}初始化下载环境")
        TaLog().info(f"{self.current_task.log_key}{self.current_task.url}")

        self.open_url(self.current_task.url)

        # 广告商列表
        selector = '//*[@data-testid="accommodation-list"]'
        wait_find_element_xpath(selector)

        # 最大页数
        try:
            if self.current_page == 1:
                selector = '//*[@data-testid="pagination"]/li'
                selector = '//*[@data-testid="pagination"]'
                pagination_ol = driver.find_element(By.XPATH, selector)
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
        driver = TaLogin().driver

        url = self.current_task.url
        if self.current_max_page != 1 and self.current_page <= self.current_max_page:
            url += f";pa-{str(self.current_page)}"
        page_info = f"page({str(self.current_page)}/{str(self.current_max_page)})"
        TaLog().info(f"{self.current_task.log_key}开始下载数据,{page_info}")
        TaLog().info(f"{self.current_task.log_key}{url}")

        self.open_url(url)

        time.sleep(self.loading_wait_time)

        waittime = 10
        waittiem_count = 0
        while waittiem_count < waittime:
            if self.loading_accommodation_list():
                break
            time.sleep(1)
            waittiem_count += 1

        if waittime <= waittiem_count:
            TaLog().error(
                f"{self.current_task.log_key}check_accommodation_list is False"
            )
            return

        selector = '//*[@data-testid="accommodation-list"]//*[@data-testid="accommodation-list-element"]'
        accommodation_list = driver.find_elements(By.XPATH, selector)

        index = 0
        outputs = []
        for accommodation in accommodation_list:
            index += 1
            output = get_accommodation_info(accommodation)
            output["Page_No"] = f"{self.current_page}-{index}"
            output["City"] = self.current_task.cityname
            output["Checkin"] = self.current_task.checkin
            output["Checkout"] = self.current_task.checkout
            output["Currency"] = self.current_task.currency

            TaLog().info(f"{self.current_task.log_key}{index}: {output}")
            outputs.append(output)
        self.current_task.output(self.output_path, outputs)
        TaLog().info(f"{self.current_task.log_key}output: {len(outputs)} lines")

    def get_code(self):
        """
        获取城市的code
        """
        temp_url = self.default_url()
        driver = self.driver
        # 调用函数生成完整的 URL
        driver.get(temp_url)

        # 创建ActionChains对象
        actions = ActionChains(driver)
        default_url = driver.current_url

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
            current_url = driver.current_url

        if current_url == default_url:
            raise ValueError(f"url not change: {default_url}")

        TaLog().info(f"{self.current_task.log_key}current_url: {current_url}")

        # 正则表达式模式
        pattern = r"hotels-(.*)\?search=(.*)"

        # 使用正则表达式查找匹配项
        match = re.search(pattern, current_url)

        if match:
            city_country = match.group(1)
            params = match.group(2)
            params = params.split(";")
            for param in params:
                if param.startswith("200-"):
                    code = param
                    break
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
            self.current_task.state = TaTask.STATE_ERROR

    def default_url(self):
        config = TaConfig().config
        template_obj = config["home_page"]["template"]
        temp_url = template_obj["url"]
        temp_url += template_obj["param"]
        default_value = template_obj["default"]
        replace_values = {
            "city_country": default_value["city_country"],
            "code": default_value["code"],
            "star": self.current_task.star_for_url(),
            "checkin": self.current_task.checkin_for_url(),
            "checkout": self.current_task.checkout_for_url(),
            "rooms": "1",
            "adults": "2",
            "child_ages": "",
        }
        temp_url = make_url(temp_url, replace_values)
        return temp_url

    def start(self, tasks: list[TaTask]):
        TaLog().info(f"start query")

        self.output_path = TaTask.output_create()

        # 开始执行爬虫
        for task in tasks:
            TaLogin().do_task(task)

        TaTask.count_task_states(tasks)

    def loading_accommodation_list(self):
        """
        查询广告商列表，如果全部加载完，返回 True
        """
        driver = TaLogin().driver

        selector = '//*[@data-testid="accommodation-list"]//*[@data-testid="accommodation-list-element"]'
        accommodation_list = driver.find_elements(By.XPATH, selector)
        for accommodation in accommodation_list:
            output = get_accommodation_info(accommodation)
            if not output["Hotelname"]:
                return False
        return True


def close_calendar():
    driver = TaLogin().driver
    actions = ActionChains(driver)
    try:
        selector = '//button[@data-testid="calendar-button-close"]'
        calendar_button_close = driver.find_element(By.XPATH, selector)
        actions.move_to_element(calendar_button_close).click().perform()
    except:
        pass


def wait_find_element_xpath(selector, waittime=10):
    driver = TaLogin().driver
    wait = WebDriverWait(driver, waittime)
    try:
        # 等待元素可见
        element = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
        return element
    except TimeoutException:
        TaLog().error(
            f"[ERROR] Timeout after {waittime}s waiting for XPath: {selector}"
        )
        return None  # 或 raise 自定义异常，视你需求而定


def make_url(temp_url: str, data: dict):
    # 使用字典的 items() 方法和循环来替换占位符
    for key, value in data.items():
        placeholder = f"{{{key}}}"
        temp_url = temp_url.replace(placeholder, str(value))
    return temp_url


def get_accommodation_info(accommodation: webelement.WebElement):
    output = {}

    config = TaConfig().config
    selectors: dict = config["selectors"]

    for output_name, selector in selectors.items():
        try:
            element = accommodation.find_element(By.XPATH, selector)
            output[output_name] = element.text

            if "Star" == output_name:
                output[output_name] = element.get_attribute("content")
        except:
            output[output_name] = ""

    selectors: dict = config["selectors2"]
    for output_name, selector in selectors.items():
        try:
            element = accommodation.find_element(By.XPATH, selector)
            if output[output_name] == "":
                output[output_name] = element.text
        except:
            pass

    if not output["Lowest booking"]:
        output["Lowest booking"] = output["Recommend booking"]
    if not output["Lowest price"]:
        output["Lowest price"] = output["Price"]
    output["Lowest booking"] = output["Lowest booking"].replace("per night on ", "")

    return output


def test():
    # $x('//*[@data-testid="modal-container"]//button')[0] 关闭注册窗口
    # 示例模板 URL
    temp_url = "https://www.trivago.hk/en-HK/srl/hotels-tokyo-japan?search=105-1318;200-71462;dr-20240525-20240527;rc-1-2;pa-24"

    driver = TaLogin().driver

    driver.get(temp_url)

    actions = ActionChains(driver)

    driver.quit()
