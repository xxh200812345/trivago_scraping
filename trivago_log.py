import yaml

import logging
import logging.config

from trivago_tool import TaConfig


class TaLog:
    _instance = None
    logger = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaLog, cls).__new__(cls)
            cls._instance.logger = logging_init()
        return cls._instance


def logging_init():
    # 获取配置
    _config = TaConfig().config
    # 打开配置文件
    with open(file=_config["logging_path"], mode="r", encoding="utf-8") as file:
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

    return logger
