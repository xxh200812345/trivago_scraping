import time
import re
import subprocess
import os
import random

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

from selenium_stealth import stealth

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
    before_currency = ""

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaLogin, cls).__new__(cls)
            cls._instance.driver = cls._instance.driver_init_chrome()
        return cls._instance

    def driver_init_chrome(self):
        TaLog().info("正在初始化 Chrome 控制器...")
        
        # 1. 读取并解析配置文件
        config = TaConfig().config
        chrome_cfg = config.get("chrome_options", {})
        TaLog().info(f"读取到 Chrome 配置: {chrome_cfg}")
        
        use_actual_browser = chrome_cfg.get("use_actual_browser", False)
        options = webdriver.ChromeOptions()
        driver = None

        # --- 统一参数配置 (无论是模式 A 还是模式 B，基础 Prefs 都可以先注入) ---
        if "prefs" in chrome_cfg:
            options.add_experimental_option("prefs", chrome_cfg["prefs"])

        if use_actual_browser:
            # ==========================================
            # 模式 A: 启动并接管真实浏览器 (Debugger 模式)
            # ==========================================
            current_dir = os.getcwd()
            user_data_path = os.path.join(current_dir, "chrome_profile")
            TaLog().info(f"当前工作目录 (CWD): {current_dir}")
            TaLog().info(f"Chrome Profile 预定路径: {user_data_path}")

            # 确保用户数据目录存在
            if not os.path.exists(user_data_path):
                TaLog().info("Profile 路径不存在，正在创建目录...")
                os.makedirs(user_data_path)
            else:
                TaLog().info("Profile 路径已存在。")

            chrome_path = chrome_cfg.get("chrome_path")
            debug_port = chrome_cfg.get("debug_port", 9222)
            TaLog().info(f"Chrome 可执行文件路径: {chrome_path}")
            TaLog().info(f"调试端口: {debug_port}")
            
            # 构造命令行启动参数
            start_cmd = [
                chrome_path,
                f"--remote-debugging-port={debug_port}",
                f"--user-data-dir={user_data_path}",
                "--no-first-run",
                "--no-default-browser-check"
            ]
            
            # 动态过滤并追加 YAML 里的额外参数，防止参数冲突
            for arg in chrome_cfg.get("arguments", []):
                if not any(x in arg for x in ["--user-data-dir", "--remote-debugging-port", "--ignore-"]):
                    start_cmd.append(arg)

            # 启动真实的物理浏览器
            TaLog().info(f"正在通过 Popen 启动物理浏览器，命令: {start_cmd}")
            subprocess.Popen(start_cmd)
            time.sleep(3)  # 留出充足时间让浏览器完全初始化

            # 核心：设置 Selenium 实验性选项去接管该端口
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            
        else:
            # ==========================================
            # 模式 B: 原生 Selenium 独立模拟模式
            # ==========================================
            TaLog().info("【标准模式】使用 Selenium 默认配置独立启动")
            for argument in chrome_cfg.get("arguments", []):
                options.add_argument(argument)

        # ==========================================
        # 统一 WebDriver 启动逻辑 (核心双保险方案)
        # ==========================================
        try:
            TaLog().info("正在启动 WebDriver (优先使用 Selenium 4 自动托管)...")
        
            # 放弃 WDM 联网下载，优先交给 Selenium 4 自动管理（接管模式下直接连 CDP 端口）
            driver = webdriver.Chrome(options=options)
            
        except Exception as e:
            TaLog().warning(f"Selenium 4 自动托管启动失败 (可能处于严格内网或打包组件丢失): {e}")

            # 计算绝对的本地驱动路径：基于当前程序运行目录的 chrome_cfg["driver_path"]["chrome"] -> res/driver/chromedriver.exe
            # 这样即使用户从外部命令行调用，也能精准定位
            base_path = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
            
            driver_path = config.get("driver_path", {})
            local_driver_path = os.path.normpath(os.path.join(base_path, driver_path["chrome"]))
            
            TaLog().info(f"正在尝试降级方案，寻找本地驱动: {local_driver_path}")
            
            if os.path.exists(local_driver_path):
                TaLog().info("成功找到指定目录下的本地驱动，正在加载...")
                service = ChromeService(executable_path=local_driver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                TaLog().error(f"在指定路径未检测到本地兜底驱动: {local_driver_path}，程序初始化中断。")
                raise e

        # ==========================================
        # 统一后置优化与防爬指纹隐藏
        # ==========================================
        # 如果是原生模拟模式，注入 CDP 隐藏自动化特征
        if not use_actual_browser:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })

        # 维持你原有的新标签页打开与切换习惯
        driver.execute_script("window.open('','_blank');")
        driver.switch_to.window(driver.window_handles[0])

        # 引入 stealth 库增强防爬混淆
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        TaLog().info("Chrome 控制器初始化完成。")
        return driver

    def set_currency(self):
        driver = self.driver
        config = TaConfig().config

        # 获取当前货币符号
        selector = '//header//*[@data-testid="header-localization-menu"]/span[1]'
        localization_menu_element = wait_find_element_xpath(selector)
        localization_menu = localization_menu_element.text
        TaLog().info(
            f"{self.current_task.log_key} {localization_menu}"
        )

        # 用货币符号找到对应的货币缩写
        currency_dict = config["currency_dict"]
        current_sign = currency_dict[self.current_task.currency]

        # 如果货币和搜索数据不一致，则改成一致
        actions = ActionChains(driver)
        if current_sign != self.before_currency:
            TaLog().info(
                f"{self.current_task.log_key}currency:  -> {self.current_task.currency}"
            )
            selector = '//header//*[@data-testid="header-localization-menu"]'
            header_localization_menu_btn = wait_find_element_xpath(selector)
            human_click(driver, header_localization_menu_btn)

            selector = f'//*[@data-testid="localization-currency-select"]'
            currency_select = wait_find_element_xpath(selector)
            time.sleep(1)
            human_click(driver, currency_select)

            # 设置成task中的货币
            select = Select(currency_select)
            select.select_by_value(self.current_task.currency)

            selector = '//dialog//button[@type="submit"]'
            dialog_apply_btn = wait_find_element_xpath(selector)
            human_click(driver, dialog_apply_btn)

            self.before_currency = current_sign

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
            
            if self.current_task.state == TaTask.STATE_ERROR:
                return

        self.current_task.state = TaTask.STATE_OVER
        TaLog().info(f"{self.current_task.log_key}end query")

    def goto_url(self):
        config = TaConfig().config
        _db = TaDB()
        city_country = None
        code = None

        # 如果excel里已经有了城市code，则直接使用
        if self.current_task.location_slug is not None:
            TaLog().info(f"{self.current_task.log_key}excel里已经有了城市code，直接使用")
            city_country  = self.current_task.location_slug
            code = self.current_task.city_code
        else:
            search_key = self.current_task.cityname
            sql = _db.tables["city"][_db.SQL_TYPE_SEARCH]
            ret = _db.to_do(TaDB.SQL_TYPE_SEARCH, sql, (search_key,))

            # 如果db中不存在code
            if len(ret) == 0:
                TaLog().info(f"{self.current_task.log_key}需要去获取城市code")
                self.get_code()

                if self.current_task.state == TaTask.STATE_ERROR:
                    return
                ret = _db.to_do(TaDB.SQL_TYPE_SEARCH, sql, (search_key,))

            city_country = ret[0][0]
            code = ret[0][1]


        template_obj = config["home_page"]["template"]
        temp_url = template_obj["url"]
        temp_url += template_obj["param"]

        replace_values = {
            "city_country": city_country,
            "code": code,
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
        """
        打开指定的URL
        """
        driver = TaLogin().driver
        driver.get(url)

        # 如果有数据
        # accommodations-counter
        selector = '//*[@data-testid="loading-animation-accommodations-counter"]'
        hotels_count = wait_find_element_xpath(selector)
        if (hotels_count is not None):
            TaLog().info(f"{self.current_task.log_key}{hotels_count.text}")
        else:

            # 如果没有数据，输出No results
            selector = '//*[@data-testid="partial-results-notification"]'
            nothing = wait_find_element_xpath(selector, waittime=5, required=False) 
            if (nothing is not None and 'No results' in nothing.text):
                TaLog().info(f"{self.current_task.log_key} No results")
                self.output_error2excel("No result(list is empty)")
                return False

            error_msg = f"{self.current_task.log_key} 没有提示No results，但是找不到酒店数据。"
            TaLog().error(error_msg)
            self.current_task.state = TaTask.STATE_ERROR
            self.output_error2excel(error_msg)
            return False

        # 关闭日期选择
        close_calendar()

        # 设置货币
        self.set_currency()

        return True

    def get_accommodation_list(self):
        """
        初始化指定条件下第一页下载列表
        """
        driver = TaLogin().driver

        TaLog().info(f"{self.current_task.log_key}初始化下载环境")
        TaLog().info(f"{self.current_task.log_key}{self.current_task.url}")
        TaLog().info(
            f"{self.current_task.log_key}search city_name: {self.current_task.cityname}"
        )

        self.current_task.record_start_time() # 记录开始查询时间
        if(self.open_url(self.current_task.url) is False):
            return
        

        # 广告商列表
        selector = '//*[@data-testid="accommodation-list"]'
        wait_find_element_xpath(selector)

        # 获取城市名称
        selector = TaConfig().config["search_area"]["cityname"]
        # 获取城市输入框
        destination_input = wait_find_element_xpath(selector)
        city_name = destination_input.get_attribute("value")
        TaLog().info(f"{self.current_task.log_key}page city_name: {city_name}")

        # 如果城市名称不一致，则报错, 如果excel已经有了城市code，则不需要检查
        if not self.current_task.location_slug:
            TaLog().info(f"{self.current_task.log_key}需要检查网页的城市和检索文件中的城市是否一致")

            if city_name.lower() != self.current_task.cityname.lower():
                TaLog().error(
                    f"{self.current_task.log_key}城市名称不一致: {city_name} != {self.current_task.cityname}"
                )
                self.current_task.state = TaTask.STATE_ERROR
                self.output_error2excel("City name is not match")
                return
            else:
                TaLog().info(f"{self.current_task.log_key}城市名称一致√")

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

        # 保证等待足够时间，防止快速访问触发限制
        config = TaConfig().config
        self.current_task.wait_until_interval(config['interval_seconds'])

        for i in range(self.current_page, self.current_max_page + 1):
            self.current_page = i
            self.accommodation_list_loop()

    def build_output_dict(self, index=None, hotel_data=None, error_msg=None):
        """
        构造统一的输出字典
        :param index: 页面中的序号（用于 Page_No）
        :param hotel_data: 单个酒店字典
        :param error_msg: 若是错误信息，传入该内容
        :return: dict
        """
        output = hotel_data.copy() if hotel_data else {}
        output["Task_No"] = f"{self.current_task.log_key}"
        output["Page_No"] = f"{self.current_page}-{index if index else 1}"
        output["City"] = self.current_task.cityname
        output["Checkin"] = self.current_task.checkin
        output["Checkout"] = self.current_task.checkout
        output["Currency"] = self.current_task.currency
        output["location_slug"] = self.current_task.location_slug
        output["city_code"] = self.current_task.city_code

        if error_msg:
            output["Hotelname"] = error_msg

        return output


    def accommodation_list_loop(self):
        """
        获取指定页面的全部广告商数据
        """
        driver = TaLogin().driver

        url = self.current_task.url
        if self.current_max_page != 1 and self.current_page <= self.current_max_page:
            url += f";pa-{self.current_page}"
        page_info = f"page({self.current_page}/{self.current_max_page})"
        TaLog().info(f"{self.current_task.log_key}开始下载数据,{page_info}")
        TaLog().info(f"{self.current_task.log_key}{url}")

        self.current_task.record_start_time() # 记录开始查询时间
        self.open_url(url)
        time.sleep(self.loading_wait_time)

        for _ in range(10):
            if self.loading_accommodation_list():
                break
            time.sleep(1)
        else:
            TaLog().error(f"{self.current_task.log_key}check_accommodation_list is False")
            return

        selector = '//*[@data-testid="accommodation-list"]//*[@data-testid="accommodation-list-element"]'
        accommodation_list = driver.find_elements(By.XPATH, selector)

        outputs = []
        for index, accommodation in enumerate(accommodation_list, start=1):
            hotel_data = get_accommodation_info(accommodation)
            output = self.build_output_dict(index=index, hotel_data=hotel_data)
            TaLog().info(f"{self.current_task.log_key}{index}: {output}")
            outputs.append(output)

        self.current_task.output(self.output_path, outputs)

        if not outputs:
            TaLog().error(f"{self.current_task.log_key}没有获取到数据")
            self.current_task.state = TaTask.STATE_ERROR
            self.output_error2excel("No result(list is empty)")
        else:
            TaLog().info(f"{self.current_task.log_key}output: {len(outputs)} lines")
            
        # 保证等待足够时间，防止快速访问触发限制
        config = TaConfig().config
        self.current_task.wait_until_interval(config['interval_seconds'])


    def output_error2excel(self, msg: str):
        """
        输出 ERROR 信息到 Excel
        """
        output = self.build_output_dict(error_msg=msg)
        self.current_task.output(self.output_path, [output])

    def get_code(self):
        """
        获取城市的code
        """
        config = TaConfig().config

        temp_url = self.default_url()
        driver = self.driver
        # 调用函数生成完整的 URL
        driver.get(temp_url)
        time.sleep(5)
        close_calendar()

        # 创建ActionChains对象
        actions = ActionChains(driver)
        default_url = driver.current_url

        # 找到指定的div元素
        selector = config["search_area"]["cityname"]
        # 获取城市输入框
        destination_input = wait_find_element_xpath(selector)

        # 模拟鼠标移动到div元素并点击
        human_click(driver, destination_input)

        # 执行键盘输入"Nagoya"
        destination_input.send_keys(self.current_task.cityname)

        # 点击第一个选项
        selector = '//*[@id="suggestion-list"]//*[@role="listbox"]//li[1]'
        first_button = wait_find_element_xpath(selector)

        human_click(driver, first_button)
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
        human_click(driver, calendar_button_close)
    except:
        pass


def wait_find_element_xpath(selector, waittime=10, required=True):
    """
    通过 XPath 查找元素并带等待机制
    :param selector: XPath 路径
    :param waittime: 等待秒数
    :param required: 是否为必选元素。如果是 False，超时将不记录错误日志
    """
    driver = TaLogin().driver
    wait = WebDriverWait(driver, waittime)
    
    try:
        # 等待元素可见
        element = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
        return element
    except TimeoutException:
        # 根据 required 参数决定日志处理方式
        if required:
            # 必选元素丢失：记录 ERROR 级别日志
            TaLog().error(
                f"[CRITICAL] Element not found (Required): {selector} (waited {waittime}s)"
            )
        return None


def make_url(temp_url: str, data: dict):
    # 使用字典的 items() 方法和循环来替换占位符
    for key, value in data.items():
        placeholder = f"{{{key}}}"
        temp_url = temp_url.replace(placeholder, str(value))
    return temp_url

def human_click(driver, element):
    actions = ActionChains(driver)
    
    # 获取元素大小，计算一个随机偏移量（不要每次都点中心）
    width = element.size['width']
    height = element.size['height']
    offset_x = random.randint(-int(width/4), int(width/4))
    offset_y = random.randint(-int(height/4), int(height/4))
    
    # 模拟人类先观察再移动
    actions.move_to_element_with_offset(element, offset_x, offset_y)
    actions.pause(random.uniform(0.2, 0.5)) # 模拟点击前的停顿
    actions.click()
    actions.perform()

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

    return output


def test():
    # $x('//*[@data-testid="modal-container"]//button')[0] 关闭注册窗口
    # 示例模板 URL
    temp_url = "https://www.trivago.hk/en-HK/srl/hotels-tokyo-japan?search=105-1318;200-71462;dr-20240525-20240527;rc-1-2;pa-24"

    driver = TaLogin().driver

    driver.get(temp_url)

    actions = ActionChains(driver)

    driver.quit()
