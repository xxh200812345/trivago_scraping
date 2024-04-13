import yaml
import logging

def logging_init():
    with open(file="config/logging.yml", mode='r', encoding="utf-8")as file:
        logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
        # print(logging_yaml)
        # 配置logging日志：主要从文件中读取handler的配置、formatter（格式化日志样式）、logger记录器的配置
        logging.config.dictConfig(config=logging_yaml)
    # 获取根记录器：配置信息从yaml文件中获取
    logger = logging.getLogger()
    # 子记录器的名字与配置文件中loggers字段内的保持一致
    my_module = logging.getLogger("my_module")
    print("rootlogger:", logger.handlers)
    print("selflogger", my_module.handlers)
    # print("子记录器与根记录器的handler是否相同：", root.handlers[0] == my_module.handlers[0])
    my_module.error("DUBUG")
    logger.info("INFO")
    return logger

logger = logging_init()