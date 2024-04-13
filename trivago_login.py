from trivago_log import logger

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

def driver_init_edge():
    logger.info(f"启动edge浏览控制器")
    #   op = Options()
    #   op.add_argument('--ignore-certificate-errors')
    #   op.add_argument('--ignore-ssl-errors')
    op = webdriver.EdgeOptions()
    #     op.add_argument(
    # '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36')
    op.add_argument('--accept-language=en')

    driver = webdriver.Edge(service=EdgeService(
        EdgeChromiumDriverManager().install()), options=op)
    driver.execute_script("window.open('','_blank');")
    driver.switch_to.window(driver.window_handles[0])
    return driver

driver = driver_init_edge()