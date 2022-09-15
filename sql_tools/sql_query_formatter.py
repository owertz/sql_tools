import argparse
import logging
import os
import re


from enum import Enum
#from tkinter import SEPARATOR

from sql_query_configuration import Constants, SQLKeywords, SQLMultiKeywords
from sql_query_formatter_test import *
from tools import readConfigFile, readFile, writeOutputFile, forwardCheckIfInORBlock
from tools import checkIfPreviousEndswithNewlineTag, configValidator, allIndex
from tools import checkMultiQueryInFile, addHook, removeHook, addSpaceAfterComma
from tools import removeNewlineTagOnLastEntry, checkIfSubstringSurroundingIsSpaces
from tools import replaceSpecificOccurencesOfSubstringInString, isFunction


__version__ = '0.0.b1'
__author__ = 'OWE'
    
"""
This script aims at formatting a SQL query in a easy-reading way, following
simple rules.


TODO
----
Legend
[ n ]: n-th task in the TODO list
[ . ]: task in progress.
[ * ]: task implemented.
[ F ]: fix implemented
[ X ]: no fix implemented + explanation

Content
[ F ] Allow the inputFile to include several SQL queries, and the formatter() to deal with it.
[ F ] Manage the comment inline (-- text ... \n) and section (/* text ... */)
[ F ] Allow the input file to start with a comment
      
FIXME
-----
[ F ] The control/management of the 3+nested blocks is not perfect: we sometime get 'spaces' 
      which aren't reduced back according to the block level.
      Dealt with the unit test myQuery6b.
[ F ] Still get a '\n' between a field name and the corresponding label. For example:

      SELECT DISTINCT 
          EP_TABLEPARAM.ID TABLEID
      FROM 
          EP_TABLEPARAM
      ;

      returns

      SELECT DISTINCT 
          ep_tableparam.id
          tableid
      FROM 
          ep_tableparam
      ;
[ F ] The "xxxx IN ('yyy', 'zzz')" does not work. See myQuery1h.
[ F ] Manage the case ORDER BY ... HAVING count(*) > ... 
[ F ] Manage properly the case: select numtie, count(*) from ...
[ F ] Cannot handle query that includes "OR" statement between "(" and ")". 
      For example: "where (numtie_1 in ('') or numtie_2 in (''))"
[ F ] LISTAGG does not work.
[ F ] GROUP BY does not work properly for all cases, e.g. "select refopn from xkd50 where senmsg='I' group by refopn order by duration desc;"
[ F ] NOT LIKE does not work properly, e.g.: "select * from pyd01 where numtie not like 'P000%';"
[ F ] Avoid capital SQL keywords when it is in table name, e.g. "select * from disctr_md_mandateoncontract;" 
      becomes: 
      SELECT
          *
      FROM
          disctr_md_mANDateoncontract
      ;
[ F ] NOT EXISTS does not work properly, e.g. "select * from pyd01 where not exists (...)
[ F ] Incorrect alignment in the following query: "select * from pyd01 where datnai > (select SUBSTR(codtb1, 1, 4) - 18|| SUBSTR(codtb1, 5, 4) from zz002);" --> doesn't handle properly the '||' [OK], ' ||' [OK], ' || ' [OK], and '|| ' [OK]. Query for testing: "select a|| sum(b) from pyd01;"
[ F ] Incorrect new line behavior for: "select x, datfin || heufin, y from tab;"

[ 1 ] Manage the query of type: SELECT ... FROM (SELECT ...)
[ F ] "select (a || sum(b)) from x;"
[ F ] "select x, count(*) from tab where trim(staan) is null group by x;"
[ 4 ] "select * from tab where x='a-b';" --> the 'a-b' should remain unchanged. Currently, it becomes 'a - b'
"""
class BasicConfiguration(Enum):
    CONFIG_FILE_NAME = "config.ini"
    VALID_LOG_LEVEL = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    VALID_KEYWORDS_CASE = ["upperCase", "lowerCase", "initCap"] # --> ["upperCase: SELECT", "lowerCase: select", "initCap: Select"]





def lowerSQLQuery(query: str, comment_open_markers=None, comment_close_markers=None) -> str:
    """Lower the query, except the content between simple and/or double quotes, and in comment (inline, section)"""
    # if comment_open_markers is not None and comment_close_markers is None:
    #     comment_close_markers = [Constants.NEW_LINE.value]

    items = ["'", '"']
    positions = []
    _comment = False
    _comment_close_marker = None
    
    for item in items:
        if item in query and query.count(item)>=2:
            #positions += [match.start() for match in re.finditer(item, query)]
            positions += allIndex(item, query)

    if positions:
        _keep = False
        query_lowered = ""
        for k, item in enumerate(query):
            if k > 0 and any([query_lowered[-len(v["open"]):] == v["open"] for v in Constants.COMMENT_MARKERS.value.values()]) and _comment_close_marker is None: #query_lowered[-2:] in comment_open_markers and not _comment:
                _comment = True
                for v in Constants.COMMENT_MARKERS.value.values():
                    if query_lowered[-len(v["open"]):] == v["open"]:
                        _comment_close_marker = v["close"]
                        break
                    else:
                        continue
            elif k > 0 and _comment and query_lowered[-len(_comment_close_marker):] == _comment_close_marker: #item == _comment_close_marker:
                _comment = False
                _comment_close_marker = None
                _keep = False
                if item != Constants.MONO_SPACE.value:
                    query_lowered += Constants.MONO_SPACE.value
            else:
                pass

            if k not in positions:
                if _keep and not _comment and not any([query_lowered[-len(m):]==m for m in comment_close_markers]):
                    query_lowered += addHook(item)
                elif _comment:
                    query_lowered += item
                else:
                    query_lowered += item.lower()
            elif k in positions and not _comment:
                _keep = not _keep
                query_lowered += item
            else:
                _keep = not _keep
                query_lowered += item.lower()
    else:
        query_lowered = query.lower()

    logging.debug(f"lowerSQLQuery: |{query_lowered}|")
    return query_lowered

def caseSQLKeywords(query: str, case=None, final=False) -> str:
    """Replace the SQL keywords with their uppercase format if required"""
    if case is None:
        case = "upperCase"

    for keyword in SQLKeywords.keywords.value:
        if case == "upperCase":
            new_keyword = keyword.upper()
        elif case == "lowerCase":
            new_keyword = keyword.lower()
        elif case == "initCap":
            new_keyword = keyword.capitalize()
        else:
            new_keyword = keyword.upper()

        if final:
            query = query.replace(keyword.upper(), new_keyword)
        else:
            #query = query.replace(keyword.lower(), new_keyword)

            _indices = allIndex(keyword.lower().strip(), query, case_sensitive=False)
            _to_compare = [Constants.MONO_SPACE.value, Constants.PARENTHESIS_OPEN.value]
            if _indices:
                _indices_case = []
                for j in _indices:                   
                    if checkIfSubstringSurroundingIsSpaces(keyword.lower().strip(), j, query, _to_compare) or isFunction(keyword.lower().strip(), j, query):
                        #query = query.replace(keyword.lower(), new_keyword)
                        _indices_case.append(j)
                    else:
                        continue
                query = replaceSpecificOccurencesOfSubstringInString(keyword.lower().strip(), _indices_case, query)                
            else:
                continue

    logging.debug(f"caseSQLKeywords: |{query}|")
    return query        

def groupMultiKeywords(query: str) -> str:
    """Replace a multiple-part keyword by its one-part equivalent (e.g., LEFT JOIN --> LEFTJOIN)"""
    for multikey, newkey in SQLMultiKeywords.keywords.value.items():
        query = query.replace(multikey.lower(), newkey)

    logging.debug(f"groupMultiKeywords: |{query}|")
    return query   

def ungroupMultiKeywords(query: str) -> str:
    """Replace a one-part equivalent keyword by the corresponding multiple-part one."""
    for multikey, newkey in SQLMultiKeywords.keywords.value.items():
        query = query.replace(newkey, multikey) 

    logging.debug(f"ungroupMultiKeywords: |{query}|")
    return query           

def addEnd(query: str) -> str:
    """Add the symbol ';' at the end of the query if not there"""
    if not query.endswith(';'):
        res = f"{query};"
    else:
        res = query
    logging.debug(f"addEnd: |{res}|")
    return res

def linearized(query: str, comment_markers= None) -> str:
    """Remove the \r, \n, \t, ... within non-comment part of the SQL query"""
    _comment = False
    _close_marker = None

    to_replace = ["\r", "\n", "\t"]
    query_linearized = ""

    query = query.strip()

    for k, item in enumerate(query):
        if k > 0 and not _comment:
            for _value in comment_markers.values():
                if query_linearized[-2:]==_value["open"]:
                    _comment = True
                    _close_marker = _value["close"]
                    if item != Constants.MONO_SPACE.value:
                        query_linearized += Constants.MONO_SPACE.value
                    break
                else:
                    continue
        elif k > 0 and _comment and _close_marker is not None and any([query_linearized[-1:]==_close_marker, query_linearized[-2:]==_close_marker]):
            _comment = False
            query_linearized = query_linearized[:-len(_close_marker)] + Constants.MONO_SPACE.value + _close_marker
            if _close_marker != Constants.NEW_LINE.value:
                query_linearized += f"{Constants.MONO_SPACE.value}{Constants.NEW_LINE.value}"
            _close_marker = None
        else:
            pass

        if _comment:
            query_linearized += item
        elif not _comment and item in to_replace:
            if any([query_linearized[-len(i):]==i for i in to_replace]):
                query_linearized += Constants.EMPTY_SPACE.value
            else:
                query_linearized += Constants.MONO_SPACE.value
        else:
            query_linearized += item

    # for v in Constants.COMMENT_MARKERS.value.values():
    #     query_linearized = query_linearized.replace(v["close"], Constants.MONO_SPACE.value + v["close"] + Constants.MONO_SPACE.value)
    
    logging.debug(f"linearized: |{query_linearized}|")
    return query_linearized

def removeMultipleSpaces(query: str) -> str:
    """Remove all the multiple spaces and replace them with a single space."""
    #return re.sub(' {2,}', ' ', query)
    replacer = {
        #" ;": ";",
        " ,": ",",
        #"(": "(",
        #")": " )",
    }
    #query = " ".join(query.split())
    query = " ".join([v for v in query.split(Constants.MONO_SPACE.value) if v])
    for key, value in replacer.items():
        query = query.replace(key, value)

    replacer_multi_to_mono_space = ["="]
    for item in replacer_multi_to_mono_space:
        query = re.sub(f" *{item} *", f" {item} ", query)

    replacer_rstrip = [";"]
    for item in replacer_rstrip:
        query = re.sub(f" *{item} *", f" {item}", query)

    query = re.sub(r' *\( *', r' \( ', query).replace('\(', '(')
    query = re.sub(r' *\) *', r' \) ', query).replace('\)', ')')

    logging.debug(f"removeMultipleSpaces: |{query}|")
    return query

def splitQuery(query:str) -> str:
    """Split the string-like input query based on single space."""
    logging.debug(f"splitQuery: |{query.split(' ')}|")
    return [item for item in query.split(' ') if len(item)>0]

def insertNewLineAndSpaces(query: list, prespaces=Constants.EMPTY_SPACE.value, block=0, newline=False):
    """
    This constitutes the main part of the formatting process. It's a recursive 
    function that can deal with as many block as you want. In this function, 
    we define all the rules to format the SQL query.

    Parameters
    ----------
    query: list 
        List of the component of the SQL query
    prespaces: str
        The prefix to apply to the query component when left-justified (increases 
        of 4 spaces at each new block)
    block: int
        The id of the block. Used to compute the prespaces and spaces strings
    newline: bool
        If true, add a new line break when starting the new block (hence at the 
        next recursion)
    """
    if isinstance(query, str):
        query = splitQuery(query)
    
    keywords_newblock = ["SELECT", "SELECTDISTINCT"]
    keywords_back = ["JOIN", "LEFTOUTERJOIN", "LEFTJOIN", "LEFTINNERJOIN", "RIGHTJOIN", "RIGHTOUTERJOIN", "RIGHTINNERJOIN", "GROUPBY"]
    keywords_backandnewline = ["FROM", "WHERE"]
    keywords_setseparator = ["MINUS"]
    keywords_nonewline = ["NOT"]
    keywords_newlineandspaces = ["AND", "WITHINGROUP", "OVER"]
    keywords_inline = ["ISNULL", "ON", "AS", "IS", "IN", "HAVING", "OR", "PARTITIONBY", "||", "THEN", "ELSE", "END", "CASE", "WHEN"]
    keywords_follow = ["LIKE", "NOTLIKE"]
    keywords_multi = {
        "ORDER": ("BY", "back"),
        "EXISTS": ("(\n", "still"),
        "NOTEXISTS": ("(\n", "still",)
        #"PARTITION": ("BY", "back"),
    }
    keywords_function = ["REPLACE", "SUBSTR", "LISTAGG", "COUNT", "DECODE", "DATEDIFF", "SUM", "AVG", "TRIM"]
    keywords_all = (
        keywords_newblock +
        keywords_back + 
        keywords_backandnewline + 
        keywords_nonewline + 
        keywords_follow + 
        list(keywords_multi.keys()) + 
        keywords_function + 
        keywords_inline + 
        keywords_newlineandspaces + 
        keywords_setseparator
    )
    keywords_join_type = [_k for _k in keywords_back if "JOIN" in _k]
    separators_strip = ["=", "<", ">"]
    separators = [Constants.SEPARATOR_COMMA.value, Constants.PARENTHESIS_OPEN.value, Constants.PARENTHESIS_CLOSE.value] + separators_strip
    #comment_start_markers = [Constants.COMMENT_INLINE_MARKER.value, Constants.COMMENT_OPENSECTION_MARKER.value]
    comment_start_markers = [v["open"] for v in Constants.COMMENT_MARKERS.value.values()]
    #comment_stop_markers = [Constants.COMMENT_CLOSESECTION_MARKER.value, Constants.NEW_LINE.value]
    #comment_stop_markers = [v["stop"] for v in Constants.COMMENT_MARKERS.value.values()]
    spaces = prespaces + Constants.FOUR_SPACES.value

    result = []

    n_block = 0

    _keywords_newblock = 0
    _open_label = False
    # _close_label = True
    _forward = False
    # _multi = ""
    _pass = False
    # _after_init_new_block = False
    # _after_keywords_newblock = False
    _after_from = False
    _btw_from_and_where = False
    _after_where = False
    _btw_from_other = False
    _btw_order_and_other = False
    _is_r8after_back_subblock = False
    _k_pass = 0
    _block_status = 0
    _within_subblock = 0
    _is_within_function = 0
    _is_within_in_block = 0
    _is_within_or_block = 0
    _latest_within = []
    _newline = newline
    _is_a_comment = False
    _comment_stop_marker = None

    _is_within_listagg = False
    _following_listagg = False
    _spaces_added_listagg = False
    _level_block_listagg = 0
    _function_within_listagg = ["OVER"]

    for k, element in enumerate(query):
        logging.debug(f"k={k:3}: element --> |{element}|")
        #print(_following_listagg, _level_block_listagg-1, _is_within_function + _is_within_or_block + _within_subblock, (Constants.SEPARATOR_COMMA.value in element or "FROM" in element), '  ', _latest_within, '  ', element)
        if (_following_listagg and _level_block_listagg-1==_is_within_function + _is_within_or_block + _within_subblock 
                and (Constants.SEPARATOR_COMMA.value in element or "FROM" in element) 
                and _spaces_added_listagg):
            spaces = Constants.MONO_SPACE.value * (len(spaces)-len(Constants.FOUR_SPACES.value))
            _following_listagg = False
            _spaces_added_listagg = False

        if k < _k_pass: # breakpoint 2 nestedSelect
            if element.strip() == Constants.PARENTHESIS_CLOSE.value and _within_subblock:
                _within_subblock -= 1
            continue
        elif element.lstrip()[:2] in comment_start_markers and not _is_a_comment: 
            for value in Constants.COMMENT_MARKERS.value.values():
                if element.lstrip()[:2] == value["open"]:
                    _is_a_comment = True
                    _comment_stop_marker = value["close"]
                    break
                else:
                    continue
            for j in range(0, k):
                if result[k-1-j].strip() != Constants.EMPTY_SPACE.value:
                    result[k-1-j] = result[k-1-j].rstrip()
                    break
                else:
                    continue
            result.append(f"{Constants.MONO_SPACE.value}{element}") 
        elif _is_a_comment and element.rstrip(Constants.MONO_SPACE.value)[-2:] == _comment_stop_marker: #in comment_stop_markers: #FIXME
            _is_a_comment = False
            _comment_stop_marker = None
            if element == Constants.NEW_LINE.value or query[k+1] == Constants.NEW_LINE.value:
                result.append(f"{element}") 
            else:
                result.append(f"{element}{Constants.NEW_LINE.value}") 
        elif _is_a_comment:
            result.append(f"{Constants.MONO_SPACE.value}{element}") 
            continue
        elif element == ";":
            if result[-1].rstrip().endswith(";"):
                pass
            elif result[k-1].rstrip(Constants.MONO_SPACE.value).endswith(Constants.NEW_LINE.value) or result[k-1]=="":
                result.append(element)
            else:
                result.append(f"{Constants.NEW_LINE.value};") 
            logging.debug(f"result: {result}")
            break                               
        elif element.endswith(Constants.QUERY_CLOSURE.value):
            result.append(element)
            logging.debug(f"result: {result}")
            break
        elif element == "(" and not _pass and result[k-1].strip() in keywords_newblock:
            _block_status += 1
            result.append(f"{spaces}{element}")
        elif element == ")" and block>0:
            if _within_subblock:
                _within_subblock -= 1
                result.append(f"{element}")
            elif not _within_subblock and _is_within_function:
                _is_within_function-=1
                result.append(f"{element}")
            else:
                _block_status -= 1
                if _block_status<1:
                    prespaces = prespaces[:-len(Constants.FOUR_SPACES.value)]
                    if result[k-1].rstrip(Constants.MONO_SPACE.value).endswith(Constants.NEW_LINE.value):
                        _nl = Constants.EMPTY_SPACE.value
                    else:
                        _nl = Constants.NEW_LINE.value
                    result.append(f"{_nl}{prespaces}{element}{Constants.NEW_LINE.value}")
                    return result, k+1
        # elif element == ")" and not _pass:
        #     _block_status -= 1
        #     result.append(f"{element}")
        else:
            if _pass:
                _pass = False
                result.append(Constants.EMPTY_SPACE.value)
                if element.strip()==Constants.PARENTHESIS_OPEN.value:
                    _within_subblock += 1

                continue

            if element.strip() in keywords_newblock and element not in keywords_newblock:
                result.append(Constants.NEW_LINE.value)
                element = element.strip()
             
            if element in keywords_newblock:
                #_keywords_newblock += 1
                n_block += 1
                if n_block>1 and result[k-1].strip() not in keywords_setseparator:
                    for _last_item in result[::-1]:
                        if len(_last_item)>0 and _last_item.strip() not in keywords_setseparator:
                            _ps = (len(_last_item)-len(_last_item.lstrip(Constants.MONO_SPACE.value))) * Constants.MONO_SPACE.value
                            break
                        else:
                            _ps = Constants.EMPTY_SPACE.value
                        
                    if "".join(result[-2:])[-2:] in ["=(", "<(", ">("] or "".join(result[-2:]) in [" IN ("]:
                        _newline = True
                        _ps += Constants.FOUR_SPACES.value
                    elif result[-1].strip() in keywords_setseparator:
                        _newline = False
                        block -= 1 # since a new call to insertNewLineAndSpaces with block+1 will be performed, but in this case, we want to keep the same value for block --> we do block-1 in such a way we finally have a call with (block-1)+1 = block
                        if len(_ps)>=len(Constants.FOUR_SPACES.value):
                            _ps = Constants.MONO_SPACE.value * (len(_ps)-len(Constants.EIGHT_SPACES.value))
                        else:
                            _ps = Constants.EMPTY_SPACE.value
                    else:
                        _newline = False 

                    _result, _k = insertNewLineAndSpaces(
                        query=query[k:], 
                        prespaces=_ps + (n_block-1) * Constants.FOUR_SPACES.value, 
                        block=block+1, #n_block-1, 
                        newline=_newline
                    )
                    _k_pass = k + _k
                    result += _result

                elif _newline:
                    if not len(result) or (len(result) and result[-1].strip() not in keywords_setseparator):
                        result.append(f"{Constants.NEW_LINE.value}{prespaces}{element}{Constants.NEW_LINE.value}")
                    else:
                        result.append(f"{prespaces}{element}{Constants.NEW_LINE.value}")
                else:
                    result.append(f"{prespaces}{element}{Constants.NEW_LINE.value}")

            elif element in keywords_back:
                _is_r8after_back_subblock = True
                if not checkIfPreviousEndswithNewlineTag(result):
                    result.append(f"{Constants.NEW_LINE.value}{prespaces}{element} ")
                else:
                    result.append(f"{prespaces}{element} ")
                #result.append(f"{prespaces}{element} ")
                
            elif element in keywords_backandnewline+keywords_setseparator:
                if element=="FROM":
                    _after_from = True
                    #_btw_from_other = True # -- goal: to be removed
                    _btw_from_and_where = True ##
                elif _after_from and element=="WHERE":
                    _after_where = True ##
                    _btw_from_and_where = False ##
                    #_btw_from_other = False # -- goal: to be removed
                elif _after_from:
                    _btw_from_other = False
                else:
                    pass

                if checkIfPreviousEndswithNewlineTag(result):
                    result.append(f"{prespaces}{element}\n")
                else:
                    result.append(f"{Constants.NEW_LINE.value}{prespaces}{element}\n")

            elif element in keywords_newlineandspaces:
                if _following_listagg and not _spaces_added_listagg:
                    spaces += Constants.FOUR_SPACES.value
                    _spaces_added_listagg = True

                if checkIfPreviousEndswithNewlineTag(result):
                    result.append(f"{spaces}{element}{Constants.MONO_SPACE.value}")
                    _forward = True
                elif query[k+1].lstrip().startswith(Constants.PARENTHESIS_OPEN.value):
                    result.append(f"{Constants.NEW_LINE.value}{spaces}{element}{Constants.MONO_SPACE.value}")
                    _forward = False
                else:
                    result.append(f"{Constants.NEW_LINE.value}{spaces}{element}{Constants.MONO_SPACE.value}")
                    _forward = True                
                
            elif element in keywords_nonewline:
                result.append(f"{spaces}{element} ") 
                _forward = True

            elif element in keywords_inline+keywords_follow:
                if checkIfPreviousEndswithNewlineTag(result):
                    result[k-1] = result[k-1].rstrip(Constants.MONO_SPACE.value)[:-1]
                    result.append(f"{Constants.MONO_SPACE.value}{element}{Constants.MONO_SPACE.value}") 
                elif result[k-1].rstrip() == Constants.PARENTHESIS_OPEN.value:
                    result.append(f"{element}{Constants.MONO_SPACE.value}")
                # elif result[k-1][-1] == Constants.MONO_SPACE.value:
                #     result.append(f"{element}{Constants.MONO_SPACE.value}") 
                else:
                    result.append(f"{Constants.MONO_SPACE.value}{element}{Constants.MONO_SPACE.value}")

                if forwardCheckIfInORBlock(query[k+2:]):
                    _forward = False
                else:
                    _forward = True            

            # elif element in keywords_follow:
            #     result[k-1] = result[k-1].replace("\n", "")
            #     result.append(f" {element} ")
            #     _forward = True

            elif element in keywords_multi.keys():
                value, alignment = keywords_multi[element]
                if alignment=="back":
                    if not checkIfPreviousEndswithNewlineTag(result[k-1]):
                        result[k-1] = result[k-1] + Constants.NEW_LINE.value
                    result.append(f"{element} {value}\n")
                elif alignment=="still":
                    result.append(f"{spaces}{element} {value}")
                else:
                    pass

                if element=="ORDER":
                    _btw_order_and_other = True
                    if result[k-2].strip()+result[k-1].strip() == "WITHINGROUP(":
                        result[k-1] = result[k-1].rstrip(Constants.NEW_LINE.value)
                        result[-1] = result[-1].rstrip() + Constants.MONO_SPACE.value
                _pass = True    

            elif element in keywords_function:
                if result[k-1].strip() in keywords_newblock or result[-1].strip() in keywords_newblock or result[k-1].strip()[-1] in (Constants.SEPARATOR_COMMA.value, Constants.PARENTHESIS_CLOSE.value):
                    if checkIfPreviousEndswithNewlineTag(result):
                        result.append(f"{spaces}{element}")
                    else:
                        result.append(f"{Constants.NEW_LINE.value}{spaces}{element}")

                elif not _after_from and not result[k-1].rstrip().endswith(Constants.SEPARATOR_COMMA.value): # Btw SELECT and FROM, to avoid 'SELECT a||\n⎵⎵⎵⎵SUM(...' and get 'SELECT a||SUM(b)...'
                    result[k-1] = result[k-1].rstrip(Constants.NEW_LINE.value)
                    result.append(f"{element}")
                    
                elif result[k-1].strip(Constants.MONO_SPACE.value).endswith(Constants.NEW_LINE.value) or result[k-1].strip(Constants.MONO_SPACE.value).endswith(Constants.SEPARATOR_COMMA.value + Constants.NEW_LINE.value):
                    #result[k-1] = result[k-1].replace(Constants.SEPARATOR_COMMA.value + Constants.NEW_LINE.value, Constants.SEPARATOR_COMMA.value)
                    #result.append(f"{Constants.MONO_SPACE.value}{element}")
                    result.append(f"{spaces}{element}")
                else:
                    result.append(f"{element}")
                #_is_within_function += 1
                if element.strip() == "LISTAGG":
                    _is_within_listagg = True
                    _level_block_listagg = _is_within_function+1 + _is_within_or_block + _within_subblock
                # elif element.strip() not in _function_within_listagg:
                #     pass

            elif _forward:
                _forward = False
                result.append(f"{element}")
                if element.strip()==Constants.PARENTHESIS_OPEN.value:
                    _within_subblock += 1                

            elif element in separators:
                #result[k-1] = result[k-1].rstrip()#.replace("\n", "") # rstrip() remove all the " ", "\n", "\t", ...
                #result.append(f"{element}")
                _temp_spaces = Constants.EMPTY_SPACE.value
                if element=="(":
                    if result[k-1].strip() in keywords_function:
                        _is_within_function += 1
                        _latest_within.append("function")
                        result[k-1] = result[k-1].rstrip()
                    elif forwardCheckIfInORBlock(query[k+1:]):
                        _is_within_or_block += 1
                        _latest_within.append("or")
                        if query[k-1] in keywords_newlineandspaces + keywords_inline: # Check whether the element before the (... OR ...) is within 'keywords_newlineandspaces' or 'keywords_inline' (e.g.:ex1: AND (... OR ...), ex2: JOIN x ON (... OR ...)). In such a case, we shouldn't add extra spaces to avoid: AND    (... OR ...)
                            _temp_spaces = Constants.EMPTY_SPACE.value
                        else:
                            _temp_spaces = spaces
                    else:
                        _within_subblock += 1
                        _latest_within.append("subblock")
                        result[k-1] = result[k-1].rstrip(Constants.NEW_LINE.value)
                    
                elif element==")":
                    if (_is_within_function + _is_within_or_block + _within_subblock) == _level_block_listagg and _is_within_listagg:
                        _following_listagg = True
                        _is_within_listagg = False

                    if _is_within_function>_within_subblock:
                        _is_within_function -= 1
                    elif _is_within_function<_within_subblock:
                        _within_subblock -= 1
                    elif _latest_within and _latest_within[-1] == "or":
                        _is_within_or_block -= 1
                    elif _latest_within and _latest_within[-1] == "in":
                        _is_within_in_block -= 1
                    elif _within_subblock > 1:
                        # Might required a better implementation
                        _within_subblock -= 1
                    else:
                        pass

                    if _latest_within:
                        _latest_within.pop()
                    result[k-1] = result[k-1].rstrip()

                else:
                    result[k-1] = result[k-1].rstrip()

                result.append(f"{_temp_spaces}{element}")

            elif result and result[k-1] in separators_strip:
                result.append(f"{element}\n")


            elif (not element.endswith(",") 
                  #and (_btw_from_other or _btw_order_and_other) #
                  and (_btw_from_and_where or _btw_order_and_other) ##
                  and element != Constants.STAR.value 
                  and (not _within_subblock or not _is_within_function)):
                if query[k+1]!=";" and query[k+1] not in keywords_all and query[k+1].strip() not in [Constants.PARENTHESIS_CLOSE.value]+separators_strip:
                    add = f"{Constants.MONO_SPACE.value}{query[k+1]}"
                    _pass = True
                elif result[k-1].rstrip() in keywords_join_type:
                    add = f"{Constants.MONO_SPACE.value}{query[k+1]}"
                    _pass = True
                else:
                    _btw_order_and_other = False
                    add = Constants.EMPTY_SPACE.value
                
                if _pass and result[k-1].strip() in keywords_back:
                    result.append(f"{element}{add}")
                elif result[k-1].strip() in keywords_back:
                    result[k-1] = result[k-1].strip(Constants.MONO_SPACE.value)
                    result.append(f"{Constants.NEW_LINE.value}{spaces}{element}{add}") 
                elif result[k-1].rstrip().endswith(Constants.SEPARATOR_COMMA.value) and query[k+1].lstrip() == Constants.PARENTHESIS_CLOSE.value:
                    result.append(f"{Constants.MONO_SPACE.value}{element}{add}{Constants.NEW_LINE.value}")
                elif any([Constants.EMPTY_SPACE.value.join(result).rstrip().endswith(_) for _ in keywords_inline]):
                    result.append(f"{Constants.MONO_SPACE.value}{element}{add}")
                elif result[k-1].endswith(Constants.PARENTHESIS_OPEN.value):
                    result.append(f"{element}{add}{Constants.NEW_LINE.value}")                 
                else: 
                    result.append(f"{spaces}{element}{add}{Constants.NEW_LINE.value}")

            elif element.startswith('"') and (element.endswith('"') or element.endswith('",')):
                _open_label = False
                result[k-1] = result[k-1].replace(Constants.NEW_LINE.value, Constants.EMPTY_SPACE.value)
                result.append(f" {element}\n")                
               
            elif element.startswith('"') and not element.endswith('"') and not _open_label:
                _open_label = True
                result[k-1] = result[k-1].replace(Constants.NEW_LINE.value, Constants.EMPTY_SPACE.value)
                result.append(f" {element}")

            elif element.endswith('"'):
                _open_label = False
                result.append(f"{element}{Constants.NEW_LINE.value}")

            elif _open_label:
                result.append(f"{element}")

            elif element==Constants.EMPTY_SPACE.value:
                result.append(f"{Constants.NEW_LINE.value}")

            elif _within_subblock or _is_within_function:
                if result[k-1].endswith(Constants.SEPARATOR_COMMA.value) and not element.startswith(Constants.MONO_SPACE.value):
                    result.append(f"{Constants.MONO_SPACE.value}{element}")
                elif Constants.SEPARATOR_COMMA.value in element:
                    result.append(f"{addSpaceAfterComma(element, hooked=True)}")
                else:
                    result.append(f"{element}")

            elif result and result[k-1] in keywords_back:
                result.append(f"{element}")

            elif element == Constants.NEW_LINE.value:
                #result.append(f"{Constants.EMPTY_SPACE.value}")
                result.append(element)
            
            elif element == Constants.STAR.value:
                if result[k-1].strip(Constants.MONO_SPACE.value).endswith(Constants.PARENTHESIS_OPEN.value):
                    result.append(element)
                else:
                    result.append(f"{spaces}{element}{Constants.NEW_LINE.value}")

            elif result and result[k-1].strip() not in keywords_all and Constants.SEPARATOR_COMMA.value not in result[k-1] and result[k-1].rstrip(Constants.MONO_SPACE.value).endswith(Constants.NEW_LINE.value):
                result[k-1] = result[k-1].rstrip(Constants.MONO_SPACE.value).replace(Constants.NEW_LINE.value, Constants.MONO_SPACE.value)
                result.append(f"{element}{Constants.NEW_LINE.value}")

            elif result and result[k-2].strip() + result[k-1].strip() == "IN(" and not _is_within_in_block:
                _is_within_in_block += 1
                _latest_within.append("in")
                result[k-1] = result[k-1].rstrip()
                result.append(f"{element.replace(Constants.MONO_SPACE.value, Constants.EMPTY_SPACE.value).replace(Constants.SEPARATOR_COMMA.value, Constants.SEPARATOR_COMMA.value + Constants.MONO_SPACE.value)}")

            elif _is_within_in_block:
                result.append(f"{element.replace(Constants.MONO_SPACE.value, Constants.EMPTY_SPACE.value).replace(Constants.SEPARATOR_COMMA.value, Constants.SEPARATOR_COMMA.value + Constants.MONO_SPACE.value)}")

            elif _is_within_or_block:
                result.append(f"{element}")

            elif _is_r8after_back_subblock:
                if result[k-1].strip() == "GROUPBY":
                    result[k-1] = result[k-1].rstrip(Constants.MONO_SPACE.value)
                    result.append(f"{Constants.NEW_LINE.value}{spaces}{element}{Constants.NEW_LINE.value}")
                else:
                    result.append(f"{spaces}{element}{Constants.NEW_LINE.value}")
                _is_r8after_back_subblock = False

            elif result[k-1].endswith(Constants.SEPARATOR_COMMA.value):
                result.append(f"{Constants.NEW_LINE.value}{spaces}{element}{Constants.NEW_LINE.value}")
            
            # elif not _after_from and not result[k-1].endswith(Constants.SEPARATOR_COMMA.value):
            #     result.append(f"{Constants.MONO_SPACE.value}{element}")

            elif not _after_from and n_block>0 and result[k-1].rstrip().endswith(Constants.PARENTHESIS_OPEN.value):
                result.append(f"{element} ")

            else:
                result.append(f"{spaces}{element}{Constants.NEW_LINE.value}")

        # Multi-query in the file
        if result and Constants.QUERY_CLOSURE.value in result[k-1].strip() and not result[k-1].strip().endswith(Constants.QUERY_CLOSURE.value):
            result[k-1] = result[k-1].strip(Constants.MONO_SPACE.value).replace(Constants.QUERY_CLOSURE.value, Constants.QUERY_CLOSURE.value + 2*Constants.NEW_LINE.value)

        logging.debug(f"_is_a_comment: {_is_a_comment}")
        logging.debug(f"result: {result}")

    #return "".join(result), k
    return result, k

def addSpacesBetweenSeparator(query: str) -> str:
    """Add spaces between a list of defined separator(s)."""
    separators = ["=", "<", ">", "-", "\|\|"]
    # for sep in separators:
    #     query = query.replace(sep, f" {sep} ")
    if Constants.HOOK_SPACE.value in query:
        query = removeHook(query, hook_type="SPACE")

    if Constants.HOOK_QUERY_CLOSURE.value in query:
        query = removeHook(query, hook_type="QUERY_CLOSURE")
    

    for sep in separators:
        query = re.sub(f" *{sep} *", f" {sep} ", query)

    query = query.replace("-  -", "--") # to account for COMMENT_INLINE_MARKER: --
    return query

def removeEscapeCharacters(query: str) -> str:
    """Remove the escape character that might still be in the result"""
    escaped_characters = ["\|\|"]
    for item in escaped_characters:
        query = query.replace(item, item.replace("\\", ""))
    return query

def formatter(query: str, show_spaces=False, inline=False, **kwargs) -> str:
    """Format a query"""
    logging.debug(f"original raw query: |{repr(query)}|")
    logging.debug(f"original query: |{query}|")
    _comment_open_markers = [Constants.COMMENT_INLINE_MARKER.value, Constants.COMMENT_OPENSECTION_MARKER.value]
    _comment_close_markers = [Constants.NEW_LINE.value, Constants.COMMENT_CLOSESECTION_MARKER.value]

    myquery = linearized(query, comment_markers=Constants.COMMENT_MARKERS.value)
    myquery = lowerSQLQuery(myquery, comment_open_markers=_comment_open_markers, comment_close_markers=_comment_close_markers)
    myquery = groupMultiKeywords(myquery)
    myquery = caseSQLKeywords(myquery, "upperCase")
    myquery = addEnd(myquery)
    myquery = removeMultipleSpaces(myquery)
    if not inline:
        myquery, _ = insertNewLineAndSpaces(myquery)
        myquery = "".join(myquery)
    myquery = addSpacesBetweenSeparator(myquery)
    myquery = ungroupMultiKeywords(myquery)
    myquery = caseSQLKeywords(myquery, kwargs.get("KEYWORDS_CASE", None), True)
    myquery = removeEscapeCharacters(myquery)
    if show_spaces:
        return myquery.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)
    else:
        return myquery

def print_expected_output(query_name:str) -> None:
    """Print an *_expected SQL query used for the unit test(s)"""
    print(globals()[f"{query_name}_expected"])

def unittest(query: str, verbose=False):
    """Make a unittest on SQL query"""
    logging.debug(f"{Constants.LINE_SEPARATOR_DASH.value}{Constants.NEW_LINE.value}UNIT TEST{Constants.NEW_LINE.value}")
    expected_output = globals()[f"{query}_expected_surrogate"]
    output = formatter(globals()[f"{query}"], True)
    logging.debug(f"Final result: {Constants.NEW_LINE.value}{output.replace(Constants.SURROGATE.value, Constants.MONO_SPACE.value)}")
    assert output==expected_output, f"\nUnit test {query} failed.\n{Constants.LINE_SEPARATOR_UNDERSCORE.value}\n\nExpected output\n{Constants.LINE_SEPARATOR_UNDERSCORE.value}\n{expected_output}\n{Constants.LINE_SEPARATOR_UNDERSCORE.value}\n\nOutput:\n{Constants.LINE_SEPARATOR_UNDERSCORE.value}\n{output}\n{Constants.LINE_SEPARATOR_UNDERSCORE.value}"
    logging.debug(f"{Constants.NEW_LINE.value}UNIT TEST COMPLETED{Constants.NEW_LINE.value}{Constants.LINE_SEPARATOR_DASH.value}{Constants.NEW_LINE.value}")

class MyParser:
    """
    A self-made parser to use with argparse when we run the script within VSC 
    to simulate a call to the script with a set of options.
    """
    def __init__(self, unitTestOnly=False, showSpaces=False, inline=False, outputFile=False, inputFile=None):
        """
        """
        self.unitTestOnly = unitTestOnly
        self.showSpaces = showSpaces
        self.inline = inline
        self.outputFile = outputFile
        if inputFile is None:
            self.inputFile = ""
        else:
            self.inputFile = inputFile


def define_argparse():
    """Define the script arguments"""
    _help = {
        "unitTestOnly": """Run the unit tests.""",
        "showSpaces": """Highlight spaces with the unicode symbol ⎵""",
        'inputFile': """Format the content of the inputFile.""",
        'outputFile': """Write the result within an output file configured in the config.ini.""",
        'inline': """Format the query on a single line"""
    }
    _description = """Format a SQL query in a readable way."""
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument('-u', '--unitTestOnly', action='store_true', help=_help['unitTestOnly'])
    parser.add_argument('-p', '--showSpaces', action='store_true', help=_help['showSpaces'])
    parser.add_argument('-i', '--inputFile', help=_help['inputFile'])
    parser.add_argument('-o', '--outputFile', action='store_true', help=_help['outputFile'])
    parser.add_argument('--inline', action='store_true', help=_help['inline'])
    return parser


def main_formatter(query):
    """Format the query"""
    if not query:
        return Constants.EMPTY_SPACE.value

    MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
    MAIN_PATH = os.path.abspath(os.path.join(MODULE_PATH, '..'))

    config = readConfigFile(os.path.join(MAIN_PATH, BasicConfiguration.CONFIG_FILE_NAME.value))
    _kwargs_configValidator = {
        "VALID_LOG_LEVEL": BasicConfiguration.VALID_LOG_LEVEL.value,
        "VALID_KEYWORDS_CASE": BasicConfiguration.VALID_KEYWORDS_CASE.value,
    }
    configValidator(config, **_kwargs_configValidator)

    LOGFILE_PATH = os.path.join(MAIN_PATH, config["LOGS_PATH"], config["LOG_FILE"])  
    LOG_LEVEL = config["LOG_LEVEL"]
    logging.basicConfig(
        level=LOG_LEVEL, 
        filename=LOGFILE_PATH, 
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.info(f"Log level: {LOG_LEVEL}")
    logging.info(f"MODULE_PATH: {MODULE_PATH}")
    logging.info(f"MAIN_PATH: {MAIN_PATH}")
    logging.info(f"LOGFILE_PATH: {LOGFILE_PATH}")
    for key, value in config.items():
        logging.info(f"config: {key}: '{value}'")
    logging.info(f"Input query: {repr(query)}")

    myqueries = checkMultiQueryInFile(query)
    result = ''
    config = {
        'KEYWORD_CASE': 'upperCase',
    }
    logging.info(f"Number of identified queries?: {len(myqueries)}")

    for key, myquery in myqueries.items():
        if len(myqueries) > 1:
            result += f"{2*Constants.NEW_LINE.value if key>0 else ''}/* Query {key+1} */{Constants.NEW_LINE.value}"

        result += formatter(myquery, show_spaces=False, inline=False, **config)
            
    return result

def main(args=None):
    """The main function to run when using it as a script"""
    MODULE_PATH = os.path.dirname(os.path.realpath(__file__))
    MAIN_PATH = os.path.abspath(os.path.join(MODULE_PATH, '..'))

    config = readConfigFile(os.path.join(MAIN_PATH, BasicConfiguration.CONFIG_FILE_NAME.value))
    _kwargs_configValidator = {
        "VALID_LOG_LEVEL": BasicConfiguration.VALID_LOG_LEVEL.value,
        "VALID_KEYWORDS_CASE": BasicConfiguration.VALID_KEYWORDS_CASE.value,
    }
    configValidator(config, **_kwargs_configValidator)

    LOGFILE_PATH = os.path.join(MAIN_PATH, config["LOGS_PATH"], config["LOG_FILE"])  
    LOG_LEVEL = config["LOG_LEVEL"]
    logging.basicConfig(
        level=LOG_LEVEL, 
        filename=LOGFILE_PATH, 
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )    

    INPUTFILE_PATH = os.path.join(MAIN_PATH, config["SQL_FILE_PATH"], config["SQL_FILE"])
    OUTPUTFILE_PATH = os.path.join(MAIN_PATH, config["SQL_FILE_PATH"], config["OUTPUT_FILE"])
    
    logging.info(f"Log level: {LOG_LEVEL}")
    logging.info(f"MODULE_PATH: {MODULE_PATH}")
    logging.info(f"MAIN_PATH: {MAIN_PATH}")
    logging.info(f"LOGFILE_PATH: {LOGFILE_PATH}")
    logging.info(f"INPUTFILE_PATH: {INPUTFILE_PATH}")
    logging.info(f"OUTPUTFILE_PATH: {OUTPUTFILE_PATH}")
    for key, value in config.items():
        logging.info(f"config: {key}: '{value}'")

    if args is None:
        parser = define_argparse()
        args = parser.parse_args()
    else:
        args = args

    logging.info(f"Script arguments: {args}")

    if args.unitTestOnly or config.get('UNITTEST', False)=='true':
        for _q in queries_for_unittest:
            unittest(_q)
        print(f"{len(queries_for_unittest)} unit tests passed successfully.\n")
        logging.info(f"{len(queries_for_unittest)} unit tests passed successfully.")
        if args.unitTestOnly:
            return None

    # myquery = "myQuery6b"
    # result = formatter(globals()[f"{myquery}"], args.showSpaces)
    # logging.debug(f"Final result: {Constants.NEW_LINE.value}{result}")

    _myqueries = "".join(readFile(INPUTFILE_PATH))
    logging.info(f"Read the file '{INPUTFILE_PATH}' and extract the query.")
    myqueries = checkMultiQueryInFile(_myqueries)
    logging.info(f"Number of query(ies) detected: {len(myqueries)}")
    logging.info("Formating process: STARTING ...")
    result = ''
    for key, myquery in myqueries.items():
        if len(myqueries) > 1:
            result += f"{2*Constants.NEW_LINE.value if key>0 else ''}/* Query {key+1} */{Constants.NEW_LINE.value}"

        result += formatter(myquery, show_spaces=args.showSpaces, inline=args.inline, **config)
        


    logging.info("Formating process: DONE")

    if args.outputFile:
        logging.info(f"Writing the result in the file '{OUTPUTFILE_PATH}'")
        writeOutputFile(result, OUTPUTFILE_PATH)
    else:
        print(result)

if __name__ == '__main__':
    myargs = None
    myargs = MyParser(unitTestOnly=False, showSpaces=True)
    main(args=myargs)
