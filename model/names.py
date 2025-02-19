class Config:
    LOOKUP_DAYS = 'lookup_days'
    END_DATE = 'end_date'
    DATE_FORMAT = 'date_format'
    INDEXES = 'indexes'
    LOCAL_CACHE = 'local_cache'


class IndexMeta:
    INDEX = 'index'
    DATE = 'Date'
    ADJ_CLOSE = 'Adj Close'
    ADJUSTED_CLOSE = 'Adjusted Close'
    LOG_RETURN = 'Log Return'
    LOG_RETURN_PERCENTAGE = 'Log Return Percentage'
    ABSOLUTE_RETURN = 'Absolute Return'
    SQUARED_RETURN = 'Squared Return'
    __ACF = 'ACF'
    ACF_LOG_RET = f'{__ACF} {LOG_RETURN}'
    ACF_ABS_RET = f'{__ACF} {ABSOLUTE_RETURN}'
    ACF_SQRT_RET = f'{__ACF} {SQUARED_RETURN}'
    VOLATILITY_EWM = 'Volatility Ewm'
    ANNUALIZED_VOLATILITY_EWM = f'Annualized {VOLATILITY_EWM}'
