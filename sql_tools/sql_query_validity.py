"""
Define a set of basic test cases to identify possible validity SQL query issues.
"""

from cgitb import reset
from enum import Enum
from pydoc import locate

#print("OWEOWE -- sql_query_validity -- ", __name__)
if __name__ in ['sql_tools.sql_query_validity', 'sql_tools.sql_tools.sql_query_validity']:
    from .sql_query_configuration import Constants
    from .tools import allIndex
else:
    from sql_query_configuration import Constants
    from tools import allIndex


class Mode(Enum):
    HARD = "hard"


def locateComment(query: str, flatten: bool =False):
    """
    Locate the position(s) of inline and multiline comments. 
    The comment markers between double quotes are not active, so will be
    ignored.
    """
    comment_indices = {}
    for key, value in Constants.COMMENT_MARKERS.value.items():
        comment_indices[key] = []
        _indices_open = allIndex(value["open"], query)
        _indices_close = allIndex(value["close"], query)
        if not _indices_open or not _indices_close:
            continue
        else:
            _temp = []
            for i in _indices_open:
                for j in _indices_close:
                    if Constants.DOUBLE_QUOTE.value in query[i:j]:
                        break
                    elif j > i and Constants.DOUBLE_QUOTE.value not in query[i:j]:
                        _temp.append((i, j + (len(value["close"])-1)))
                        break
                    else:
                        continue
        comment_indices[key] = _temp
        
    if flatten:
        comment_indices_inline = []
        for r in comment_indices.values():
            comment_indices_inline += r
        return comment_indices_inline
    else:
        return comment_indices


def cleanQuery(query: str, mode=None):
    """
    Remove all non relevant content from the query. For example, 
    Input: 
        select numtie as "id(", numcli "other" from table -- my comment
        where z='test(' exists (select null from w);

    output (HARD):
        select numtie as, numcli from table where z= exists (select null from w);
    """
    if mode is None:
        mode = Mode.HARD.value

    _in_comment = False
    _in_value = False
    
    indices_comments = locateComment(query, flatten=True)
    N = len(indices_comments)
    K = 0

    result = str()
    for k, character in enumerate(query):
        if mode == Mode.HARD.value:
            if character in [Constants.SIMPLE_QUOTE.value, Constants.DOUBLE_QUOTE.value] and not _in_value:
                _in_value = True
                continue
            elif character in [Constants.SIMPLE_QUOTE.value, Constants.DOUBLE_QUOTE.value] and _in_value:
                _in_value = False
                continue
            elif not _in_comment and indices_comments and indices_comments[K][0] <= k <= indices_comments[K][1]:
                _in_comment = True
                continue
            elif _in_comment and k-1 == indices_comments[K][1]:
                K += 1
                if K<N and k == indices_comments[K][0]: # in case a comment section directly follows the previous one
                    continue
                else:
                    _in_comment = False
                    result += character
            elif not _in_value and not _in_comment:
                result += character
            else:
                continue
        else:
            result += character

    result = result.replace(Constants.NEW_LINE.value, Constants.MONO_SPACE.value)
    return result


class Validator():
    """Dto for the query validation"""
    def __init__(self, query: str):
        self.query = query
        self.bracket = None

    def validateBracket(self):
        """
        Check whether the number of open and close brackets matches, 
        excluding the comments and values.
        """
        result = {}
        query = cleanQuery(self.query)
        for key, value in Constants.BRACKET_REPERTOIRE.value.items():
            result[key] = query.count(value["open"]) == query.count(value["close"])

        self.bracket = all(result.values())


def main():
    """Main function to run"""
    query = "select w as \"Mytest\", t \"--\" from x where -- inline ] comment \n exists (select null from z where w = '('); /* multiline { comment \n multiline comment () *//* another comment*/"
    print(query)
    print('')

    validator = Validator(query)
    validator.validateBracket()
    print(validator.bracket)

if __name__ == "__main__":
    main()