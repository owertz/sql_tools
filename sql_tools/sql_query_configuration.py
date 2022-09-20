import logging
import os
from pyexpat.errors import messages
import re

from enum import Enum

__version__ = '0.0.b4'
__author__ = 'OWE'

"""
This file contains a set of SQL queries used to perform unit testing on 'sql_query_formatter.py' script.


TODO
----
Legend
[ n ]: n-th task in the TODO list
[ . ]: task in progress.
[ * ]: task implemented.

Content
[  ] ...
      
FIXME
-----
-
"""


class Messages(Enum):
    QUERY_NOT_SUPPORTED = "Sorry, but only the SELECT/type queries are currently supported"


class Constants(Enum):
    """Define some constants"""
    HOOK_SPACE = u'\u02eb'
    HOOK_QUERY_CLOSURE = u'\u00ac'
    EMPTY_SPACE = ""
    MONO_SPACE = " "
    FOUR_SPACES = 4 * MONO_SPACE
    EIGHT_SPACES = 8 * MONO_SPACE
    TWELVE_SPACES = 12 * MONO_SPACE
    SURROGATE = u'\u23b5'
    NEW_LINE = "\n"
    SEPARATOR_COMMA = ","
    STAR = "*"
    PARENTHESIS_OPEN = "("
    PARENTHESIS_CLOSE = ")"
    QUERY_CLOSURE = ";"
    DOUBLE_QUOTE = "\""
    SIMPLE_QUOTE = "'"
    LINE_SEPARATOR_DASH = 80 * "-"
    LINE_SEPARATOR_UNDERSCORE = 80 * "_"
    COMMENT_INLINE_MARKER = "--"
    COMMENT_OPENSECTION_MARKER = "/*"
    COMMENT_CLOSESECTION_MARKER = "*/"
    COMMENT_MARKERS = {
        "inline": {
            "open": "--",
            "close": NEW_LINE
        },
        "section": {
            "open": "/*",
            "close": "*/"
        },
    }


class RegularExpressions(Enum):
    MULTI_SPACES = '( +)'


class SQLKeywords(Enum):
    keywords = [
        "SELECT",
        "UPDATE",
        "DELETE",
        "FROM",
        "JOIN",
        "LEFT",
        "OUTER",
        "INNER",
        "WHERE",
        " ON ",
        "AND",
        "EXISTS",
        "NOT",
        "SUBSTR",
        "ORDER BY",
        "NULL",
        "LIKE",
        " DESC",
        " ASC",
        " COUNT",
        "REPLACE",
        " AS ",
        " IS ",
        "DISTINCT",
        "LISTAGG",
        "DECODE",
        "PARTITION",
        "WITHIN",
        "GROUP ",
        " IN ",
        "MINUS",
        "HAVING",
        " OR ",
        "OVER",
        "||",
        "SUM",
        "THEN",
        "ELSE",
        "END",
        "AVG",
        "DATEDIFF",
        "ISNULL",
        "CASE",
        "WHEN",
        "TRIM",
    ]

class SQLMultiKeywords(Enum):
    keywords = {
        "LEFT JOIN": "LEFTJOIN",
        "LEFT OUTER JOIN": "LEFTOUTERJOIN",
        "LEFT INNER JOIN": "LEFTINNERJOIN",
        "RIGHT JOIN": "RIGHTJOIN",
        "RIGHT OUTER JOIN": "RIGHTOUTERJOIN",
        "RIGHT INNER JOIN": "RIGHTINNERJOIN",
        "INNER JOIN": "INNERJOIN",
        "WITHIN GROUP": "WITHINGROUP",
        "SELECT DISTINCT": "SELECTDISTINCT",
        "GROUP BY": "GROUPBY",
        "PARTITION BY": "PARTITIONBY",
        "NOT LIKE": "NOTLIKE",
        "NOT EXISTS": "NOTEXISTS",
        "IS NOT": "ISNOT",
        #"ORDER BY": "ORDERBY",
    }
        

    def main():
        """Main function used when running the file"""
        print(SQLKeywords.keywords.value)


    if __name__ == "__main__":
        main()