import pandas as pd
from pandas import DataFrame


class Index:

    def __init__(self, index_name: str, index_ticker: str, data: pd.DataFrame):
        self.i_name = index_name
        self.i_ticker = index_ticker
        self.df = data
        self.daily_info: DataFrame = DataFrame()
        self.volatility: DataFrame = DataFrame()
        self.monthly_info: DataFrame = DataFrame()
        self.acf_log: DataFrame = DataFrame()
        self.acf_abs: DataFrame = DataFrame()
        self.acf_sqrt: DataFrame = DataFrame()

    def __str__(self):
        return f'{{name: {self.i_name}, ticker: {self.i_ticker}, data_size:{self.df.size}}}'

    def __repr__(self):
        return self.__str__()



