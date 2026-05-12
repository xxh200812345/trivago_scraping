import yaml
import logging
import logging.config
import os
from trivago_tool import TaConfig

class TaLog:
    _instance = None
    logger = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaLog, cls).__new__(cls)
            cls._instance.logger = logging_init()
        return cls._instance
    
    # 优化：支持 *args 和 **kwargs，这样可以使用 self.logger.info("msg %s", var)
    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)


def logging_init():
    config = TaConfig().config
    
    # 确保日志目录存在（如果不存在，TimedRotatingFileHandler 会报错）
    log_dir = config.get("logging_dir", "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    with open(file=config["logging_path"], mode="r", encoding="utf-8") as file:
        logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
        logging.config.dictConfig(config=logging_yaml)

    wdm_logger = logging.getLogger("WDM")
    logger = logging.getLogger("trivago_logic")
    return logger