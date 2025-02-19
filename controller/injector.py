import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import statsmodels.api as sm
import numpy as np
import yfinance as yf
from model.index import Index
import pandas as pd

from model.names import Config, IndexMeta


class Injector:
    __DEFAULT_YEARS = 2
    __DEFAULT_LOOKUPS = __DEFAULT_YEARS * 365
    __DEFAULT_END = datetime.today()
    __DEFAULT_DATE_FORMAT = '%Y-%m-%d'
    __LINES = '-----------------------------------------------------------'

    def __init__(self, conf_file: str):
        self.indexes: list[Index] = []
        self.__inject_data_from_yahoo(conf_file)
        self.__setup_daily_data()
        self.__setup_monthly_data()
        self.__setup_volatility_ewm()
        self.__setup_index()
        pass

    def __inject_data_from_yahoo(self, conf_file):

        try:
            with open(conf_file, 'r', encoding='utf-8') as file_conf:
                config = json.load(file_conf)
                print(config)
                lookup_days = config.get(Config.LOOKUP_DAYS, Injector.__DEFAULT_LOOKUPS)
                end_date = config.get(Config.END_DATE, Injector.__DEFAULT_END)
                date_format = config.get(Config.DATE_FORMAT, Injector.__DEFAULT_DATE_FORMAT)
                start_date = (end_date - timedelta(days=lookup_days)).strftime(date_format)
                end_date = end_date.strftime(date_format)
                index_list = config.get(Config.INDEXES, None)
                for index in index_list:
                    from_yahoo = yf.download(
                        index_list[index],
                        start=start_date,
                        end=end_date,
                        auto_adjust=False
                    )
                    from_yahoo = pd.DataFrame({key[0]: value for key, value in from_yahoo.items()})
                    from_yahoo.reset_index(inplace=True)
                    from_yahoo.rename(columns={IndexMeta.INDEX: IndexMeta.DATE}, inplace=True)
                    from_yahoo.rename(columns={IndexMeta.ADJ_CLOSE: IndexMeta.ADJUSTED_CLOSE}, inplace=True)
                    from_yahoo[IndexMeta.DATE] = from_yahoo[IndexMeta.DATE].dt.date
                    index_bean = Index(index_name=index,
                                       index_ticker=index_list[index],
                                       data=from_yahoo)
                    print(index_bean.df.columns)
                    self.indexes.append(index_bean)

        except FileNotFoundError:
            print(f"file {file_conf} not found")
            exit(-1)
        except json.JSONDecodeError:
            print("Error in decoding json")
            exit(-1)
        except AttributeError:
            print("some attribute is None")
            exit(-1)

    def __setup_daily_data(self):

        for index in self.indexes:
            index.daily_info = pd.DataFrame(index.df[IndexMeta.DATE])

            index.daily_info[IndexMeta.LOG_RETURN] = np.log(
                index.df[IndexMeta.ADJUSTED_CLOSE] / index.df[IndexMeta.ADJUSTED_CLOSE].shift(1)
            )

            index.daily_info[IndexMeta.ABSOLUTE_RETURN] = index.df[IndexMeta.ADJUSTED_CLOSE].pct_change().abs()
            index.daily_info[IndexMeta.SQUARED_RETURN] = np.square(index.df[IndexMeta.ADJUSTED_CLOSE].pct_change())
            index.daily_info.set_index(IndexMeta.DATE, inplace=True)
            index.daily_info.index = pd.to_datetime(index.daily_info.index)
            index.daily_info.dropna(inplace=True)
            index.daily_info[IndexMeta.LOG_RETURN_PERCENTAGE] = index.daily_info[IndexMeta.LOG_RETURN] * 100

            # ACF for log return
            acf_values = sm.tsa.acf(index.daily_info[IndexMeta.LOG_RETURN], nlags=30)
            index.acf_log = pd.DataFrame({
                IndexMeta.ACF_LOG_RET: acf_values
            }, index=range(len(acf_values)))

            # ACF for absolute return
            acf_values = sm.tsa.acf(index.daily_info[IndexMeta.ABSOLUTE_RETURN], nlags=30)
            index.acf_abs = pd.DataFrame({
                IndexMeta.ACF_ABS_RET: acf_values
            }, index=range(len(acf_values)))
            # ACF for squared return
            acf_values = sm.tsa.acf(index.daily_info[IndexMeta.SQUARED_RETURN], nlags=30)
            index.acf_sqrt = pd.DataFrame({
                IndexMeta.ACF_SQRT_RET: acf_values
            }, index=range(len(acf_values)))

    def __setup_monthly_data(self):
        for index in self.indexes:
            dummy = pd.DataFrame(index.daily_info)
            dummy = dummy[dummy.index.is_month_end]
            index.monthly_info = dummy

        pass

    # Calcoliamo la volatilià usando ewma
    def __setup_volatility_ewm(self, lam=0.90) -> None:
        """
        :param lam: indicate the effort for older data
        """
        for index in self.indexes:
            dummy = pd.DataFrame(index.daily_info[[IndexMeta.LOG_RETURN_PERCENTAGE]])
            dummy_ewm = np.sqrt(dummy.ewm(span=1 / (1 - lam)).var())
            index.volatility = dummy_ewm
            index.volatility.columns = [IndexMeta.VOLATILITY_EWM]
            index.volatility[IndexMeta.ANNUALIZED_VOLATILITY_EWM] = (index.volatility[IndexMeta.VOLATILITY_EWM]
                                                                     * np.sqrt(252))

    def print_indexes(self):
        print(Injector.__LINES)
        print("Analyzing this index list: {")
        for index in self.indexes:
            print(f'\t{index}')
        print(f'}}\n{Injector.__LINES}')

    def get_multi_index(self) -> pd.DataFrame:
        ret: pd.DataFrame
        concat = []
        columns = []
        for index in self.indexes:
            concat.append(index.daily_info[IndexMeta.LOG_RETURN_PERCENTAGE])
            columns.append(index.i_name)
        ret = pd.concat(concat, axis=1)
        ret.columns = columns
        ret.dropna(inplace=True)
        return ret

    def local_cache(self):
        for index in self.indexes:
            index.df.to_csv(f"{Config.LOCAL_CACHE}{os.sep}{index.i_name.split(' ')[0]}#{index.i_ticker}.csv")

    def __setup_index(self):
        for index in self.indexes:
            index.df.set_index('Date', inplace=True)

    def get_indexes_names(self) -> list[str]:
        ret = []
        for index in self.indexes:
            ret.append(index.i_name)
        return ret
