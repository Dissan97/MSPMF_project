import os

from controller.garch_model import Analyzer
from controller.injector import Injector
import matplotlib.pyplot as plt
from arch import arch_model
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri
import mgarch

from model.names import IndexMeta

os.environ['R_LANGUAGE'] = 'en_US.UTF-8'
if __name__ == '__main__':

    # Check if rugarch is installed, and if not, install it
    if not rpackages.isinstalled('rugarch') or not rpackages.isinstalled('rmgarch'):
        raise RuntimeError('rugarch missing')
    loader = Injector(conf_file='config/config.json')
    loader.local_cache()
    return_map = {}
    # print(loader.indexes[0].volatility)
    # print(loader.indexes[0].daily_log_return_percentage)
    print(loader.indexes[0].daily_info)
    print(loader.get_multi_index())
    pandas2ri.activate()
    multi_index = loader.get_multi_index()
    print(multi_index)
    r_returns = pandas2ri.py2rpy(multi_index)
    ro.globalenv['returns'] = r_returns
    #analyzer = Analyzer(loader=loader)
    #analyzer.fit()
    #analyzer.summary()
    """ro.r('''
        Sys.setlocale("LC_CTYPE", "en_US.UTF-8")
        library(rmgarch)
        library(rugarch)
    
        # Caricare i dati dal Python (già passati in "returns")
        returns <- as.data.frame(returns)
        print(returns)
    ''')
    """

    print(loader.indexes[0].acf_log)
    print(loader.indexes[0].acf_abs)
    print(loader.indexes[0].acf_sqrt)
    """plt.figure(figsize=(12, 6))
    plt.stem(loader.indexes[0].acf[IndexMeta.ACF_LOG_RET].index, loader.indexes[0].acf[IndexMeta.ACF_LOG_RET])
    plt.show()"""
    """plt.plot(loader.indexes[0].daily_return.index, loader.indexes[0]
             .daily_return['Log Return Percentage'])

    plt.show()"""

'''    model = arch_model(loader.indexes[0].daily_return['Log Return'], vol='GARCH', p=1, q=1)

    garch_fit = model.fit()
    print(f"Results for\n")
    print(garch_fit.summary())
    garch_fit.plot()
'''
