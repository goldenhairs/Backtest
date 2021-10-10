import pandas as pd
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

from Backtest.server.algorithm.stupid import StupidAlgorithm
from Backtest.server.db.db_networth import NetWorthDB
from Backtest.server.db.db_backtest import BacktestDB
from Backtest.server.util.tools import DateTools
from Backtest.server.util.exceptions import NonTradingError
from Backtest.server.util.log import get_logger


logger = get_logger(__file__)
networth_db = NetWorthDB()
backtest_db = BacktestDB()


class AutomaticInvestmentPlan(ABC):

    InvestmentCycles = [180, 365, 1095]

    @abstractmethod
    def create_algo(self):
        # factory method
        pass

    def invest_with_start_interval(self, code, start_interval, end, cycle=None):
        """
        每周定投 起始日为一个区间
        须确保end为交易日，起始区间内的非交易日会被自动剔除 

        :param code:             基金代码            str       '005827'
        :param start_interval:   定投开始日          (datetime, datetime)     ('2021-01-08', '2021-02-23')
        :param end:              定投结束日          str       '2021-08-09'
        :param cycle:            投资周期，仅作为标记  int        180 365 365*3
        :return df                                  dataframe
        """

        df = pd.DataFrame(columns=['start', 'week', 'algorithm', 'cycle', 'profit_rate', 'test_date'])

        stupid = self.create_algo(code)
        
        for start in DateTools.get_between_data(start_interval[0], start_interval[1]):
            try:
                stupid.prepare_data(start, end) 
            except NonTradingError as error:
                logger.debug(f"Start:{start} is non-trading day, continue.")
                continue

            res = stupid.invest_weekly()
            for index, rate in enumerate(res):
                df = df.append({'start': start, 
                                'week': index+1,
                                'algorithm': 'stupid',
                                'cycle': cycle,
                                'profit_rate': rate,
                                'test_date': datetime.now()
                                }, ignore_index=True)
        logger.info(f"统计完成:{code}, 起始日区间为{start_interval}, 结束日为{end}.")
        return df

    def analysis_realtime(self, code, cycle, size=60):
        '''
        距离今天指定时间前（半年、一年、三年）的定投分析

        :param code:             基金代码         str     '005827'
        :param cycle:            投资周期         int     180
        :param size:             起始区间大小      int     60
        :return df                               dataframe
        '''
        release_date = networth_db.release_date(code)
        last_date = networth_db.last_date(code)

        # 处理起始区间，如果起始点在发行日之前，就调整为发行日那天
        start_interval = DateTools.get_before_date_interval(cycle, size)
        start = start_interval[0]
        if start < release_date:
            start_interval = (release_date,
                              release_date + timedelta(days=size)
                              )
            logger.warning(f"基金:{code}, 起始日:{start} 超过首发日:{release_date}, "
                           f"start_interval修复为{start_interval}.")

        # 处理结束的那天，如果结束的那天在数据库里还没上传，就调整为数据库中最后的日子
        end = DateTools.get_recent_trading_day(datetime.today())
        if end > last_date:
            end = last_date
            logger.debug(f"基金:{code}, 结束日在数据库中不存在, 修复为{end}.")

        logger.info(f"开始统计，{code} 前{cycle}天每周定投，区间大小:{size}"
                    f" 起始区间:{start_interval}, 结束日:{end}.")

        df = self.invest_with_start_interval(code, start_interval, end, cycle)
        return df


class StupidPlan(AutomaticInvestmentPlan):

    def create_algo(self, code):
        return StupidAlgorithm(code)


def upload_backtest_data(code):
    """
    向 db_backtest 数据库上传基金的，半年、一年、三年回测数据
    有新的计划就向 aip_plans 中加
    """
    aip_plans = [StupidPlan()]

    try:
        for plan in aip_plans:
            backtest_df = pd.DataFrame()
            for cycle in plan.InvestmentCycles:
                df = plan.analysis_realtime(code=code, cycle=cycle)
                backtest_df = pd.concat([backtest_df, df])

            backtest_db.to_sql(code, backtest_df)
            logger.info(f"Upload backtest data({code}) success.")
        return True

    except Exception as error:
        logger.error(f"Upload backtest data occur error:{error}.")
        return False


if __name__ == "__main__":
    
    upload_backtest_data("005669")





