import yaml
import os

class TaConfig:
    _instance = None
    # Path to the configuration file
    CONFIG_PATH = 'config/trivago_web.yml'

    city_dict = {}
   
    config = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaConfig, cls).__new__(cls)
            cls._instance.config = cls._instance.get_config(TaConfig.CONFIG_PATH)
        return cls._instance

    def get_config(cls, path):
        '''
        Get configuration from a YAML file.
        '''
        # Open the YAML file and load its contents
        with open(path, 'r', encoding="utf-8") as stream:
            return yaml.safe_load(stream)

    @staticmethod
    def ensure_file_exists(file_path):
        """
        Ensure that the specified file path exists. If the file or directories do not exist, create them.

        :param file_path: The path of the file to check or create.
        """
        # 检查文件路径是否存在
        if not os.path.exists(file_path):
            # 如果文件路径不存在，则创建文件夹（如果需要的话）
            os.makedirs(os.path.dirname(file_path), exist_ok=True)





