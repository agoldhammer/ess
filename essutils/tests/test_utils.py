from essutils import utils
import pandas as pd

def test_get_immigration_data():
    imm = utils.get_data(utils.IMMDATA)
    assert "dweight" in imm.columns


def test_weighted_value_counts():
    testdata = {'x1': [10, 20, 25], 'x2': [1, 2, 7]}
    testdf = pd.DataFrame(testdata)
    s = utils.weighted_value_counts(testdf, normalize=True)
    assert(s[25] == 0.7)
