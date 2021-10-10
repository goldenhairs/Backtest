import os
import json
import threading


class Config(object):

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            with Config._instance_lock:
                if not hasattr(Config, "_instance"):
                    Config._instance = object.__new__(cls)  
        return Config._instance

    def __init__(self):
        config_path = os.getenv('CONFIG_PATH', None)
        if not config_path:
            raise Exception("Please add env-variable:CONFIG_PATH to ~/bash_profile")
        self.json_data = self._read_from_json(config_path)

    def _read_from_json(self, path):
        with open(path) as file:
            json_data = json.load(file)
        return json_data

    @property
    def server_port(self):
        # 服务的端口
        return self.json_data.get("SERVER_PORT")

    @property
    def db_username(self):
        # 数据库账号
        return self.json_data.get("DB_USERNAME")

    @property
    def db_password(self):
        # 数据库密码
        return self.json_data.get("DB_PASSWORD")

    @property
    def db_address(self):
        # 数据库连接地址
        return self.json_data.get("DB_ADDRESS")

    @property
    def db_port(self):
        # 数据库连接端口
        return self.json_data.get("DB_PORT")

    @property
    def db_backtest(self):
        # 存放基金回测数据
        return self.json_data.get("DB_BACKTEST")

    @property
    def db_networth(self):
        # 存放基金净值的数据库
        return self.json_data.get("DB_NETWORTH")

    @property
    def log_path(self):
        # 日志配置文件路径
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.conf")
