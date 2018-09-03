import pandas as pd
# import numpy as np
# import matplotlib
import matplotlib.pyplot as plt
import altair as alt
#  from pprint import pprint

IMMDATA = "~/Prog/EurSocSur/data/immdata.csv"


questions = {'acetalv': ['Ppl of min race/eth in area',
                         '1-alm none, 3-many, 789-ref/dk/na'],
             'eimpcnt': ['Alw many/few from poorer cntrys',
                         '1-many, 4-none, 789-ref/dk/na'],
             'gvrfgap': ['Govt shd judge generously',
                         '1/5-agr/dis, 789-ref/dk/na'],
             'imbleco': ['Imm take more than put',
                         '0-take more, 9-put more'],
             'imdetbs': ['Boss diff race/eth',
                         '0-dont mind, 9-mind a lot'],
             'imdetmr': ['Imm marry close rel',
                         '0-dont mind, 9-mind a lot'],
             'imtcjob': ['Imm take/create jobs',
                         '0-take, 9-create'],
             'imwbcrm': ['Imm make crime worse/better',
                         '0-worse, 9-better'],
             'lwdscwp': ['Anti-disc law good/bad',
                         '0-bad, 9-good'],
             'noimbro': ['Estimate num', 'do not use'],
             'pplstrd': ['Share tradition good',
                         '1-agree str, 5-dis str'],
             'qfimchr': ['Qualif Christian',
                         '0-unimp, 10-imprtnt'],
             'qfimcmt': ['Qualif cmtd way of life',
                         '0-unimp, 10-imprtnt'],
             'qfimedu': ['Qualif edu',
                         '0-unimp, 10-imprtnt'],
             'qfimlng': ['Qualif lang',
                         '0-unimp, 10-imprtnt'],
             'qfimwht': ['Qualif white',
                         '0-unimp, 10-imprtnt'],
             'qfimwsk': ['Qualif skills',
                         '0-unimp, 10-imprtnt']}


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
    year = '2002' if rnd == 1 else '2014'
    var = df.columns[1]
    annot = questions[var]
    return alt.Chart(df).mark_bar().encode(
        alt.X(var, scale=alt.Scale(domain=[0, 1])),
        y='cntry',
        order=alt.Order('response', sort='ascending'),
        color=alt.Color(
            'response:O',
            legend=alt.Legend(title='Response'),
            scale=color_scale)
    ).properties(title=f"{annot[0]} * {year} * {annot[1]}")


def df2responses(dfin, cntry, rnd, var):
    """
    Arrange weighted value counts for subsequent processing
    :dfin : source dataframe (imm)
    :cntry: country to process
    :return: dataframe of weighted response data for country
    """

    edata = get_wtd_val_cts(dfin, cntry, rnd, var)
    edata.rename_axis("response", inplace=True)
    df = edata.to_frame()
    df["cntry"] = cntry
    df['essrnd'] = rnd
    df = df.reset_index()
    return df


def countries_to_plotting_frame(dfin, countries, rnd, var):
    """
    Rearrange data in form suitable for plotting
    :dfin : source data frame (imm)
    :countries: list of countries to plot
    :rnd: int, round number, 1 or 7
    :var: string, name of var to plot
    :return: dataframe of weighted responses
    """

    return pd.concat([df2responses(dfin, cntry, rnd, var) for cntry
                      in countries])


def plot_group(dfin, countries, rnd, var):
    """
    Plot graph of var for countries and rnd
    :dfin : the source data frame (imm)
    :countries: list of countries to include
    :rnd: round number, integer 1 or 7
    :var: string, variable to graph
    :return: Altair chart
    """

    df = countries_to_plotting_frame(dfin, countries, rnd, var)
    chart = plot_stacked_bars(df)
    with alt.data_transformers.enable('json'):
        chart.to_dict()
    return chart


def duoplot(df, countries, var):
    """
    Horizontall concatenate rnds 1 and 7 of graph of var
    :df : source data frame (imm)
    :countries: list of countries
    :return: horizontall concatenated Altair charts
    """

    chart1 = plot_group(df, countries, 1, var)
    chart2 = plot_group(df, countries, 7, var)
    return alt.hconcat(chart1, chart2)


def multigroup_plot(df, groups, var):
    """
    Vertically concatenate paired plots from several groups
    :df : source dataframe (imm)
    :return: vertically concatenated Altair paired plots
    """

    charts = [duoplot(df, group, var) for group in groups]
    return alt.vconcat(*charts)
