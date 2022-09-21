#print("OWEOWE -- test_sample -- ", __name__)
if __name__ == "__main__":
    from sql_tools.sql_query_formatter import formatter
    from sql_tools.sql_query_configuration import Constants

    from sql_tools_test.sql_query_formatter_test import *
else:
    from ..sql_tools.sql_query_formatter import formatter
    from sql_tools.sql_tools_test.sql_query_formatter_test import *


def test_myQuery1a():
    result = formatter(myQuery1a, show_spaces=True)
    assert result == myQuery1a_expected_surrogate

def test_myQuery1b():
    result = formatter(myQuery1b, show_spaces=True)
    assert result == myQuery1b_expected_surrogate

def test_myQuery1c():
    result = formatter(myQuery1c, show_spaces=True)
    assert result == myQuery1c_expected_surrogate

def test_myQuery1d():
    result = formatter(myQuery1d, show_spaces=True)
    assert result == myQuery1d_expected_surrogate

def test_myQuery1e():
    result = formatter(myQuery1e, show_spaces=True)
    assert result == myQuery1e_expected_surrogate

def test_myQuery1f():
    result = formatter(myQuery1f, show_spaces=True)
    assert result == myQuery1f_expected_surrogate

def test_myQuery1g():
    result = formatter(myQuery1g, show_spaces=True)
    assert result == myQuery1g_expected_surrogate

def test_myQuery1h():
    result = formatter(myQuery1h, show_spaces=True)
    assert result == myQuery1h_expected_surrogate

def test_myQuery1i():
    result = formatter(myQuery1i, show_spaces=True)
    assert result == myQuery1i_expected_surrogate

def test_myQuery1j():
    result = formatter(myQuery1j, show_spaces=True)
    assert result == myQuery1j_expected_surrogate

def test_myQuery1k1():
    result = formatter(myQuery1k1, show_spaces=True)
    assert result == myQuery1k1_expected_surrogate

def test_myQuery1k2():
    result = formatter(myQuery1k2, show_spaces=True)
    assert result == myQuery1k2_expected_surrogate

def test_myQuery1k3():
    result = formatter(myQuery1k3, show_spaces=True)
    assert result == myQuery1k3_expected_surrogate

def test_myQuery1k4():
    result = formatter(myQuery1k4, show_spaces=True)
    assert result == myQuery1k4_expected_surrogate

def test_myQuery1m():
    result = formatter(myQuery1m, show_spaces=True)
    assert result == myQuery1m_expected_surrogate

def test_myQuery2a():
    result = formatter(myQuery2a, show_spaces=True)
    assert result == myQuery2a_expected_surrogate

def test_myQuery2b():
    result = formatter(myQuery2b, show_spaces=True)
    assert result == myQuery2b_expected_surrogate

def test_myQuery2c():
    result = formatter(myQuery2c, show_spaces=True)
    assert result == myQuery2c_expected_surrogate

def test_myQuery3a():
    result = formatter(myQuery3a, show_spaces=True)
    assert result == myQuery3a_expected_surrogate

def test_myQuery3b():
    result = formatter(myQuery3b, show_spaces=True)
    assert result == myQuery3b_expected_surrogate

def test_myQuery4a():
    result = formatter(myQuery4a, show_spaces=True)
    assert result == myQuery4a_expected_surrogate

def test_myQuery4b():
    result = formatter(myQuery4b, show_spaces=True)
    assert result == myQuery4b_expected_surrogate

def test_myQuery4c():
    result = formatter(myQuery4c, show_spaces=True)
    assert result == myQuery4c_expected_surrogate

def test_myQuery5a():
    result = formatter(myQuery5a, show_spaces=True)
    assert result == myQuery5a_expected_surrogate

def test_myQuery5b():
    result = formatter(myQuery5b, show_spaces=True)
    assert result == myQuery5b_expected_surrogate

def test_myQuery5c():
    result = formatter(myQuery5c, show_spaces=True)
    assert result == myQuery5c_expected_surrogate

def test_myQuery5d():
    result = formatter(myQuery5d, show_spaces=True)
    assert result == myQuery5d_expected_surrogate

def test_myQuery5e():
    result = formatter(myQuery5e, show_spaces=True)
    assert result == myQuery5e_expected_surrogate

def test_myQuery5f():
    result = formatter(myQuery5f, show_spaces=True)
    assert result == myQuery5f_expected_surrogate

def test_myQuery5g():
    result = formatter(myQuery5g, show_spaces=True)
    assert result == myQuery5g_expected_surrogate

def test_myQuery5h():
    result = formatter(myQuery5h, show_spaces=True)
    assert result == myQuery5h_expected_surrogate

def test_myQuery5i():
    result = formatter(myQuery5i, show_spaces=True)
    assert result == myQuery5i_expected_surrogate

def test_myQuery6a():
    result = formatter(myQuery6a, show_spaces=True)
    assert result == myQuery6a_expected_surrogate

def test_myQuery6b():
    result = formatter(myQuery6b, show_spaces=True)
    assert result == myQuery6b_expected_surrogate

def test_myQuery7a():
    result = formatter(myQuery7a, show_spaces=True)
    assert result == myQuery7a_expected_surrogate

def test_myQuery7b():
    result = formatter(myQuery7b, show_spaces=True)
    assert result == myQuery7b_expected_surrogate

def test_myQuery7c():
    result = formatter(myQuery7c, show_spaces=True)
    assert result == myQuery7c_expected_surrogate

def test_myQuery10a():
    result = formatter(myQuery10a, show_spaces=True)
    assert result == myQuery10a_expected_surrogate

def test_myQuery20a():
    result = formatter(myQuery20a, show_spaces=True)
    assert result == myQuery20a_expected_surrogate

if __name__ == "__main__":
    print(formatter("select * from pyd01;"))
    test_myQuery1a()