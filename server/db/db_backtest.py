import threading
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import DateTime, DECIMAL, INT, VARCHAR

from Backtest.server.util.config import Config


config = Config()


class BacktestDB():

    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(BacktestDB, "_instance"):
            with BacktestDB._instance_lock:
                if not hasattr(BacktestDB, "_instance"):
                    BacktestDB._instance = object.__new__(cls)  
        return BacktestDB._instance

    def __init__(self):
        self.engine = create_engine(
            f"mysql+pymysql://{config.db_username}:{config.db_password}"
            f"@{config.db_address}:{config.db_port}/{config.db_backtest}"
        )

        self.columns = {'start': VARCHAR(64),
                        'week': INT,
                        'algorithm': VARCHAR(64),
                        'cycle': INT,
                        'profit_rate': DECIMAL(5, 4),
                        'test_date': DateTime
                        }

    def _table_name(self, code):
        return f"tbl_{code}"

    def to_sql(self, code, df):

        df.to_sql(name=self._table_name(code),
                  con=self.engine,
                  if_exists="replace",
                  index=False,
                  dtype=self.columns)
        return self._table_name(code)

    def read_sql(self, code):
        return pd.read_sql(self._table_name(code), self.engine)
