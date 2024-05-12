import yaml

class TaConfig:
    _instance = None
    # Path to the configuration file
    CONFIG_PATH = r'trivago_scraping\config\trivago_web.yml'
   
    config = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # 添加成员变量
        self.config = self.get_config(self.CONFIG_PATH)


    def get_config(cls, path):
        '''
        Get configuration from a YAML file.
        '''
        # Open the YAML file and load its contents
        with open(path, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)






