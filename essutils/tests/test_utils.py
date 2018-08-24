from essutils import utils

def test_get_immigration_data():
    imm = utils.get_immigration_data()
    assert "dweight" in imm.columns
