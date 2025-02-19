import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

from model.names import IndexMeta


def multi_plot_in_row(dfs: list[pd.DataFrame], info=IndexMeta.LOG_RETURN_PERCENTAGE,
                      fig_size=(20, 30), plot_names=None):
    if plot_names is None:
        plot_names = ["plot"]
    fig, axs = plt.subplots(len(dfs), 1, figsize=fig_size)
    i = 0
    for df in dfs:
        sns.lineplot(x=df.index, y=df[info], ax=axs[i], color='blue')
        axs[i].set_title(f'{plot_names[i%len(plot_names)]}')
    plt.show()
