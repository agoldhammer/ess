import pandas as pd
# import numpy as np
# import matplotlib
import matplotlib.pyplot as plt

IMMDATA = "~/Prog/EurSocSur/data/immdata.csv"


def get_data(filename):
    """
    Load ESS immigration data
    :param filename: name of file to load, str
    :returns: dataframe
    """

    df = pd.read_csv(filename)
    return df


def weighted_value_counts(x, normalize=False):
    """
    weight value counts in first column by weights in second column of x
    :x: dataframe, values in first column, weights in second
    :normalize: normalize the counts (sum 1), default False
    :return: weighted value counts, indexed in descending order
    :rtype: series
    """

    c0 = x.columns[0]
    c1 = x.columns[1]
    xtmp = x[[c0, c1]].groupby(c0).agg({c1: 'sum'}).sort_values(c1,
                                                                ascending=False)
    s = pd.Series(index=xtmp.index, data=xtmp[c1], name=c0)
    if normalize:
        s = s / x[c1].sum()
    return s


def barplot(df, var, countries=None):
    """
    Make normalized weighted barplot of var
    :df: dataframe in which var occurs
    :var: var to plot
    :countries: list of countries to plot, None (default) means plot all
    :return: none
    """

    vars = ['acetalv', 'eimpcnt', 'gvrfgap', 'imbleco', 'imdetbs',
            'imdetmr', 'imtcjob', 'imwbcrm', 'lwdscwp', 'noimbro',
            'pplstrd', 'qfimchr', 'qfimcmt', 'qfimedu', 'qfimlng',
            'qfimwht', 'qfimwsk']
    assert(var in vars)
    if not countries:
        countries = df.cntry.unique()
    for c in countries:
        data = df[(df.cntry == c)]
        fig, axes = plt.subplots(1, 2, sharex=True, sharey=True)
        for round, ax_num in [(1, 0), (7, 1)]:
            rdata = data[data.essround == round]
            qout = weighted_value_counts(rdata[[var, "pspwght"]],
                                         normalize=True)
            qout = qout.sort_index()
            ax = axes[ax_num]
            if not qout.empty:
                ax.set_title(f"{var} \n for country {c} round {round}")
                qout.plot(ax=ax, kind="bar")
            else:
                ax.set_title(f"No data for {var}\n country {c} round {round}")
        plt.show()
