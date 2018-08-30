import pandas as pd
# import numpy as np
# import matplotlib
import matplotlib.pyplot as plt
import altair as alt
#  from pprint import pprint

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
    xtmp = x[[c0, c1]].groupby(c0).agg({c1: 'sum'}).\
        sort_values(c1, ascending=False)
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


def get_wtd_val_cts(df, cntry, round, var):
    """
    Get weighted value counts for var and (country, round) in df
    :df: The data frame to work on, should be imm for this notebook
    :cntry: the country, string
    :round: essround, int 1 or 7
    :return: weighted counts; if cntry missing, returns empty frame
    :rtype: Series
    """
    if cntry not in df.cntry.unique():
        raise ValueError(f"Country {cntry} not in dataset")
    if round not in df.essround.unique():
        raise ValueError(f"Round {round} not in dataset")
    if var not in df.columns:
        raise ValueError(f"Variable {var} not in dataset")
    grouped = df.groupby(['cntry', 'essround'])[[var, 'pspwght']]
    try:
        s = weighted_value_counts(grouped.get_group((cntry, round)),
                                  normalize=True)
    except KeyError:  # handle case of missing country data
        s = pd.Series(data=[0], index=[0], name=var)
        s.index.name = var
    s = s.sort_index(ascending=True)
    return s


color_scale = alt.Scale(
            domain=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 77, 88, 99],
            range=["red", "indianred", "salmon", "darkorange",
                   "yellow", 'skyblue', "dodgerblue", "steelblue",
                   'blue', 'midnightblue', "darkmagenta",
                   "gray", "silver", "mistyrose"])


def plot_stacked_bars(df):
    rnd = df.essrnd.iloc[0]
    var = df.columns[1]
    return alt.Chart(df).mark_bar().encode(
        alt.X(var, scale=alt.Scale(domain=[0, 1])),
        y='cntry',
        order=alt.Order('response', sort='ascending'),
        color=alt.Color(
            'response:O',
            legend=alt.Legend(title='Response'),
            scale=color_scale)).properties(title=f"Graph of {var} round {rnd}")


def df2responses(dfin, cntry, rnd, var):
    edata = get_wtd_val_cts(dfin, cntry, rnd, var)
    edata.rename_axis("response", inplace=True)
    df = edata.to_frame()
    df["cntry"] = cntry
    df['essrnd'] = rnd
    df = df.reset_index()
    return df


def countries_to_plotting_frame(dfin, countries, rnd, var):
    return pd.concat([df2responses(dfin, cntry, rnd, var) for cntry
                      in countries])


questions = ['acetalv', 'eimpcnt', 'gvrfgap', 'imbleco',
             'imdetbs', 'imdetmr', 'imtcjob', 'imwbcrm',
             'lwdscwp', 'noimbro', 'pplstrd', 'qfimchr',
             'qfimcmt', 'qfimedu', 'qfimlng', 'qfimwht', 'qfimwsk']


def plot_group(dfin, countries, rnd, var):
    df = countries_to_plotting_frame(dfin, countries, rnd, var)
    chart = plot_stacked_bars(df)
    with alt.data_transformers.enable('json'):
        chart.to_dict()
    return chart
