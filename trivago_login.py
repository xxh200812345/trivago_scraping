import time

from trivago_log import TaLog
from trivago_task import TaTask

from selenium import webdriver
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
    driver = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaLogin, cls).__new__(cls)
            cls._instance.driver = cls._instance.driver_init_edge()
        return cls._instance

    def driver_init_edge(self):
        _logger = TaLog().logger
        _logger.info(f"启动edge浏览控制器")
        #   op = Options()
        #   op.add_argument('--ignore-certificate-errors')
        #   op.add_argument('--ignore-ssl-errors')
        op = webdriver.EdgeOptions()
        #     op.add_argument(
        # '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36')
        op.add_argument("--accept-language=en")

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
        logger = TaLog().logger
        stime = 0
        time.sleep(sleeptime)
        if self.is_bot_wait():
            logger.info("反爬虫中...")
        # $x("")
        while self.is_bot_wait():
            time.sleep(1)
            # 超过31s依旧还在读取
            if stime > 31:
                self.driver.refresh()
                logger.info("超过31s依旧还在读取,刷新页面")
                stime = 0
                time.sleep(6)
            stime += 1
        if stime > 0:
            logger.info("反爬虫结束")

    def do_task(self, task: TaTask):
        """
        单独处理每一个task
        """
        logger = TaLog().logger
        logger.info(f"{task.log_key}start query")
        logger.info(f"{task}")
