import yaml

class TaConfig:
    _instance = None
    # Path to the configuration file
    CONFIG_PATH = r'trivago_scraping\config\trivago_web.yml'

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
        with open(path, 'r') as stream:
            return yaml.safe_load(stream)






