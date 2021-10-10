import threading
import pandas as pd
from sqlalchemy import create_engine

from Backtest.server.util.config import Config


config = Config()


class NetWorthDB():

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(NetWorthDB, "_instance"):
            with NetWorthDB._instance_lock:
                if not hasattr(NetWorthDB, "_instance"):
                    NetWorthDB._instance = object.__new__(cls)  
        return NetWorthDB._instance

    def __init__(self):
        self.engine = create_engine(
            f"mysql+pymysql://{config.db_username}:{config.db_password}"
            f"@{config.db_address}:{config.db_port}/{config.db_networth}"
        )

    def _table_name(self, code):
        return f"tbl_{code}"

    def read_sql(self, code):
        return pd.read_sql(self._table_name(code), self.engine)

    def query_sql(self, sql):
        """
        sql = f"select * from table;"
        """
        return pd.read_sql_query(sql, self.engine)

    def release_date(self, code):
        # 为数据库中第一条
        pd = self.read_sql(code)
        return pd.iloc[0]['date']

    def last_date(self, code):
        # 为数据库中最后一条
        pd = self.read_sql(code)
        return pd.iloc[-1]['date']
