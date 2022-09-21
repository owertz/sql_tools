"""
Define a set of basic test cases to identify possible validity SQL query issues.
"""

#print("OWEOWE -- sql_query_validity -- ", __name__)
if __name__ in ['sql_tools.sql_query_validity', 'sql_tools.sql_tools.sql_query_validity']:
    from .sql_query_configuration import Constants
else:
    from sql_query_configuration import Constants


def validityBracket(query: str):
    """Check whether the number of open and close brackets matches."""
    return True