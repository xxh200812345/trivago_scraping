import yaml

import logging
import logging.config

from trivago_tool import TaConfig

class TaLog:
    _instance = None
    logger = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # 添加成员变量
        self.logger = logging_init()
        
def logging_init():
    # 获取配置
    _config = TaConfig().config
    # 打开配置文件
    with open(file=_config['logging_path'], mode='r', encoding="utf-8") as file:
        logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
        # 配置logging日志
        logging.config.dictConfig(config=logging_yaml)

    # 获取根记录器
    logger = logging.getLogger()
    # 获取子记录器
    my_module = logging.getLogger("my_module")

    # 打印日志处理器信息
    print("Root logger handlers:", logger.handlers)
    print("My module logger handlers:", my_module.handlers)

    # 测试日志输出
    my_module.error("ERROR message from my_module")
    logger.info("INFO message from root logger")
    
    return logger

