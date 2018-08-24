import pandas as pd

def get_immigration_data():
    """
    Load ESS immigration data
    :param none:
    :returns: dataframe
    """

    imm = pd.read_csv("~/Prog/EurSocSur/data/immdata.csv")
    return imm
