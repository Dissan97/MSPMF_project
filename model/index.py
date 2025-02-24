import pandas as pd
from pandas import DataFrame
from model.names import IndexMeta as im


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

    def get_df_by_name(self, col_name=im.ADJUSTED_CLOSE) -> pd.DataFrame | None:

        if col_name in self.df.columns:
            return self.df[col_name]
        elif col_name in self.daily_info.columns:
            return self.daily_info[col_name]
        elif col_name in self.volatility.columns:
            return self.volatility[col_name]
        return None
