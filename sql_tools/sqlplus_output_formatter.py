import argparse
from enum import Enum
import logging
from operator import ge
import os
import subprocess

from tools import writeOutputFile, readConfigFile

__version__ = '1.0.0'
__author__ = 'OWE'
    
"""
This script aims at running a SQL query via SQLPLUS and produce an 
output file including the result in a human-readable way. 


TODO
----
Legend
[ n ]: n-th task in the TODO list
[ . ]: task in progress.
[ * ]: task implemented.

Content
[ 1 ] The current version doesn't handle the query other than 
      'select * from ...'. One should manage the case where only a 
      part of the fields are selected in the query. For exemple:
      'select A, B from ...'.
      
[ * ] The configuration and constants should be put in a config.ini 
      file and read by the script.
      
[ 3 ] Should add a check on the size of the SQLPLUS result before 
      starting the formatting process --> avoid running forever on 
      millions of lines.
      
[ 4 ] Should be able to handle several 'select' queries and create 
      an output file per query.
      
[ * ] It should accept, as input, a file that contains the output 
      of a SQLPLUS run. In such a way, we can run the script over
      an output file in case we cannot run the script on the machine 
      on which runs SQLPLUS (e.g. when Python3 isn't installed on 
      such machine).
      
[ 6 ] Add the SEPARATOR in the config.py configuration file.
      
FIXME
-----
[ F ] Bug when the header lies on one line.
[ 2 ] Manage the "x rows selected." at the end of the output
[ 3 ] Some data are replaced by Null while correctly passed as an input
"""


# SQL CONFIGURATION
SQL_TEMP_FILENAME = '_temp.sql' 
SELECT = 'select'
SEPARATOR = '@@s@@'
EMPTY_FIELD = 'Null'

QUERIES = {
    'get_column_names': "select column_name from all_tab_cols where table_name='{}';",
    'set_numwidth': "SET NUMWIDTH 20",
    'set_separator': "SET COLSEP '{}'".format(SEPARATOR),
    "set_chunksize": "SET LONGCHUNKSIZE 999999",
    "set_pagesize": "SET PAGESIZE 0",
    "set_linesize": "SET LINESIZE 500",
    "get_the_count": "select count(*) from {table} {where_clause};",
    "get_all_user_tables": "select TABLE_NAME, TABLESPACE_NAME, STATUS, INI_TRANS, MAX_TRANS, INITIAL_EXTENT, NEXT_EXTENT, MIN_EXTENTS, MAX_EXTENTS, LOGGING, BACKED_UP, NUM_ROWS, BLOCKS, EMPTY_BLOCKS, AVG_SPACE, CHAIN_CNT, AVG_ROW_LEN, AVG_SPACE_FREELIST_BLOCKS, NUM_FREELIST_BLOCKS, DEGREE, INSTANCES, CACHE, TABLE_LOCK, SAMPLE_SIZE, LAST_ANALYZED, PARTITIONED from user_tables;",
    "get_all_notempty_user_tables": "select TABLE_NAME, TABLESPACE_NAME, STATUS, INI_TRANS, MAX_TRANS, INITIAL_EXTENT, NEXT_EXTENT, MIN_EXTENTS, MAX_EXTENTS, LOGGING, BACKED_UP, NUM_ROWS, BLOCKS, EMPTY_BLOCKS, AVG_SPACE, CHAIN_CNT, AVG_ROW_LEN, AVG_SPACE_FREELIST_BLOCKS, NUM_FREELIST_BLOCKS, DEGREE, INSTANCES, CACHE, TABLE_LOCK, SAMPLE_SIZE, LAST_ANALYZED, PARTITIONED from user_tables where NUM_ROWS>0;",
    "get_user_tables": "select TABLE_NAME, TABLESPACE_NAME, STATUS, INI_TRANS, MAX_TRANS, INITIAL_EXTENT, NEXT_EXTENT, MIN_EXTENTS, MAX_EXTENTS, LOGGING, BACKED_UP, NUM_ROWS, BLOCKS, EMPTY_BLOCKS, AVG_SPACE, CHAIN_CNT, AVG_ROW_LEN, AVG_SPACE_FREELIST_BLOCKS, NUM_FREELIST_BLOCKS, DEGREE, INSTANCES, CACHE, TABLE_LOCK, SAMPLE_SIZE, LAST_ANALYZED, PARTITIONED from user_tables where table_name='{}';",
}

DB_ISSUES = {
    'ERROR': {
        'ORA-': {
            'en': 'Generic issue',
        },
        'no result': {
            'de': 'Es wurden keine Zeilen ausgewahlt',
        },
        # 'ORA-28000': {
        #     'de': 'Account ist gesperrt',
        # },
        # 'ORA-12162': {
        #     'en': 'TNS:net service name is incorrectly specified',
        # },
    },
    'WARNING': {},

}

WORDING_N_RESULT_RETURN = {
    'de': 'Zeilen ausgewahlt',
    }

class Constants(Enum):
    """Define some constants"""
    OUTPUT_ENDING = [
        "rows selected", 
        "row selected",
    ]
    NEW_LINE = "\n"

# FUNCTIONS

def readFile(filename, root=None):
    """
    Read a file.
    
    Parameters
    ----------
    filename: str
        Name of the file to read.

    root: str
        The absolute root path to the file to read.
    """
    if root is None:
        root = ""
    result = []
    with open(os.path.join(root, filename), 'r') as f:
        for _line in f.readlines():
            result.append(_line)
    return result
    
def defineLanguageSpecificConfig(language='de'):
    """
    Define language-specific constants and configuration. 
 
    Parameters
    ----------
    language: str (default: 'de')
        Defines the language to consider, e.g. 'de', 'en', 'fr', 'nl'.
    
    """
    config = {}
    config['QUERY_N_RESULT_RETURN'] = WORDING_N_RESULT_RETURN[language]
    return config
    
def generateValidFormatedPath(path):
    """
    """
    if not ' ' in path:
        return path
        
    path_split = path.split('/')
    valid_path = ['\'{}\''.format(_part) if ' ' in _part else _part for _part in path_split]
    return '/'.join(valid_path)

def isDBIssue(line, errors=None, warnings=None):
    """
    Check if the line contains an ORA-type error id, which would indicates 
    either a WARNING or an ERROR when dealing with the DB.
    """
    if errors is None and warnings is None:
        return False
    else:
        if errors is not None:
            for _e in errors:
                if _e in line:
                    logging.error('DB ERROR {} FOUND'.format(_e))
                    return True

        if warnings is not None:
            for _w in warnings:
                if _w in line:
                    logging.warning('DB WARNING {} FOUND'.format(_w))
                    return False

    return False

def getTableName(query):
    """
    Extract the table name out of a simple 'select'-SQL query.
    
    Parameters
    ----------
    query: str
        For example, query = 'select * from PT1TAB order by PT1_RNID;'
    """
    if 'where' in query:
        table = query.split('from ')[1].split(' where')[0].split(';')[0].replace(' ', '')
    elif 'where' not in query:
        table = query.split('from ')[1].strip().split(' ')[0].strip().replace(';', '')
    else:
        table = ''
    return table

def getWhereClause(query: str) -> str:
    """
    Extract the WHERE-clause from the query.
    """
    if "where" in query:
        return "WHERE {}".format(query.split('where')[1].split(';')[0].strip())
    else:
        return ''

def getField(query, query_type='select'):
    """
    Extract the fields out of a simple 'select'-SQL query. When all the fields
    are requested (e.g. select * from ...), a list containing only 
    '_all_fields_' is returned. 

    Parameters
    ----------
    query: str
        For example, query = 'select * from PT1TAB order by PT1_RNID;'  

    query_type: str
        By default, only the 'select' is relevant.  
    """
    fields = query.split('from')[0].split(query_type)[1].strip()
    if fields == '*':
        return ["_all_fields_"]
    else:
        return [_value.strip().upper() for _value in fields.split(',')]

def extractInfoFromSelectQuery(query):
    """
    Extract several information out of a simple 'select'-SQL query.

    Parameters
    ----------
    query: str
        For example, query = 'select * from PT1TAB order by PT1_RNID;'    
    """
    result = {}
    result["table_name"] = getTableName(query)

    fields = getField(query)
    if len(fields)==1 and fields[0]=="_all_fields_":
        result["fields"] = None
    else:
        result["fields"] = fields

    result["where_clause"] = getWhereClause(query)
    return result


def generateSQLfile(query, sql_temp_path_filename=None):
    """
    Generate a temporarily SQL file to run with SQLPLUS, that contains 
    additional parametrization/configuration.
    
    Parameters
    ----------
    query: str
        The main query to run. Additional parametrization/configuration
        is added.
    """
    if sql_temp_path_filename is None:
        sql_temp_path_filename = ""
    #with open(SQL_TEMP_PATH_FILENAME.replace('\'', ''), 'w+') as f:
    with open(os.open(sql_temp_path_filename.replace('\'', ''), os.O_CREAT | os.O_WRONLY, 0o777), 'w+') as f:
       f.write(QUERIES['set_numwidth'] + '\n')
       f.write(QUERIES['set_separator'] + '\n')
       #f.write(QUERIES['set_chunksize'] + '\n')
       #f.write(QUERIES['set_pagesize'] + '\n')
       #f.write(QUERIES['set_linesize'] + '\n')
       f.write(query + '\n') 
    return None

def runSQLcommand(command):
    """
    Run a SQLPLUS command.
    
    Parameters
    ----------
    command: str
        The shell command that could be run in a shell window, which includes 
        a call to SQLPLUS. For example:
        command = 'echo exit | sqlplus -s {env} @{sqlFile}'
        where {env} is the environment DB configuration and {sqlFile} the 
        absolute/relative path pointing to a *.sql file to run.
    """
    _p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    a, b = _p.communicate()
    return a.decode('utf-8'), b

def runSQLquery(query, env_config=None, db_err=None):
    """
    Run a SQL query using SQLPLUS on a given DB. The configuration of the DB 
    is defined within the ENV_CONFIG variable, in the `DB CONFIGURATION` 
    section.
    
    Parameters
    ----------
    query: str
        Simple query passed to SQLPLUS to be run.    
    """
    if env_config is None:
        env_config = ""
    
    if db_err is not None:
        NO_OUTPUT = db_err
    else:
        NO_OUTPUT = None

    _sqlplus = 'echo "{q}" | sqlplus -s {env}'.format(env=env_config, q=query.replace('\n', ''))
    _p = subprocess.Popen(_sqlplus, stdout=subprocess.PIPE, shell=True)
    a, b = _p.communicate()
    a, b = a.decode('utf-8'), b
    if NO_OUTPUT is not None and NO_OUTPUT in a:
        b = NO_OUTPUT
    return a, b

def getCount(query: str, env_config: str) -> None:
    """
    Get the count(*) of rows that are returned by the SQL query. 
    """
    result = extractInfoFromSelectQuery(query)
    q = QUERIES["get_the_count"].format(table=result["table_name"], where_clause=result["where_clause"])
    logging.debug(f"[DEBUG getCount: q: {q} ]")
    _result, _e = runSQLquery(q, env_config=env_config)
    logging.debug(f"[DEBUG getCount: _result: {_result} ]")
    count = int(_result.split('----------')[1].strip())
    return count

def extractColumnNames(content):
    """
    Extract the column names from the result obtained when running the query 
    QUERIES['get_column_names']. The table name is passed when calling 
    runSQLquery().
    
    Parameters
    ----------
    content: list
        List of string, resulting from the SQLPLUS run of the query    
        QUERIES['get_column_names']
    """
    cn = 'COLUMN_NAME'
    K = -1
    i_lastEmptyLineSinceLastcn = -1
    read_cn = False
    result = []
    for k, line in enumerate(content):
        if line.startswith(cn):
            read_cn = True
            K = k+2
        elif K>0 and k>=K:
            if len(line)>0:
                result.append((k, line))
            else:
                if read_cn:
                    i_lastEmptyLineSinceLastcn = k
                    read_cn = False
    return [_r for _id, _r in result if _id<i_lastEmptyLineSinceLastcn] 
    
def extractCroppedColumnNames(content, with_index=False):
    """
    Extract the (possibly cropped) column names directly from the SQLPLUS 
    output content.
    
    Parameters
    ----------
    content: list of str
        List of strings that compose the header of a SQLPLUS output, 
        and which includes the SEPARATOR. For example:
        content = [
            '  PT2_SQID@@s@@  PT2_RNID@@s@@  PT2_SUSY@@s@@  PT2_INST@@s@@  PT2_STAT',
            '----------@@s@@----------@@s@@----------@@s@@----------@@s@@----------',
            '  PT2_VDDT@@s@@P@@s@@P',
            '----------@@s@@-@@s@@-'
            ]
    """
    logging.debug('[DEBUG extractCroppedColumnNames: content: {} ]'.format(content))
    column_names = []
    column_names_indexes = {}
    K = 0
    for k, _line in enumerate(content):
        if not _line.startswith('-'):
            logging.debug('[DEBUG extractCroppedColumnNames: _line: {} ]'.format(_line))
            if SEPARATOR in _line:
                column_names += [_t.strip() for _t in _line.split(SEPARATOR) if len(_t.strip())>0]
            else:
                _column_names_for_the_current_line = [_t for _t in _line.split(' ') if len(_t)>0]
                column_names += _column_names_for_the_current_line
                if with_index:
                    column_names_indexes[K] = []
                    _k = 0
                    for _cln in _column_names_for_the_current_line:
                        _idx = _line[_k:].index(_cln) + _k #+ len(_cln)
                        column_names_indexes[K].append(_idx)
                        _k = _idx
                    K += 1

    for key, value in column_names_indexes.items():
        assert len(value)==len(set(value)), f"The column_names_indexes must be a list of unique indices. Duplicate found in {key}: {value}"
    
    if with_index:
        column_names_dict = {}
        _t = 0
        for key, value in column_names_indexes.items():
            column_names_dict[key] = column_names[_t:_t+len(value)]
            _t += len(value)


        return column_names, column_names_dict, column_names_indexes
    else:
        return column_names

def appendLine(part, line, lines, counter, N, n_field=None, debug=False):
    """
    One table record, hereafter a 'line', is detected as complete when all the 
    fields for this record have been extracted from the SQLPLUS result. 
    If a line is complete, it is appended to the list 'lines' that collect
    all the lines, hence all the table records extracted from the SQLPLUS
    query run. 
    
    If not complete, the line is completed with the 'part'. It may require
    several iteration with several 'part's to get a complete line, hence the 
    use of the counter wrt the number 'N' of expected fields. 
    
    Parameters
    ----------
    part: str
        Record extracted from the SQLPLUS output content, which is not part of 
        the cropped header.

    line: str
        The current state of the line, possibly composed of several parts (when
        the cropped header is extended on more than 1 record (2 when including 
        the separator-record.

    lines: list
        List of completed lines, depending of the cropped header size. 
        
    counter: int
        Current number of fields collected in the 'line'. If the counter 
        is lower than the expected number of fields, the 'part' is added to 
        the 'line'. Otherwise, the 'line' is appended to the list of lines.
        
    N: int
        Number of expected fields, based on the COLUMN_NAME.
    """
    if counter<N:
        logging.debug('[DEBUG appendLine: --> line not yet completed: {} ]'.format(line))
        if not part.endswith(SEPARATOR):
            part = part + SEPARATOR
        line += part + ' '
        counter += 1
    else:
        logging.debug('[DEBUG appendLine: --> append the completed line: {} ]'.format(line))
        if line.rstrip().endswith(EMPTY_FIELD+SEPARATOR) and n_field is not None and line.count(SEPARATOR)==n_field+1:
            line = line[:-len(EMPTY_FIELD+SEPARATOR)]
        elif line.rstrip().endswith(SEPARATOR) and n_field is not None and line.count(SEPARATOR)<n_field:
            line += (n_field - line.count(SEPARATOR)) * (EMPTY_FIELD+SEPARATOR)
        lines.append(line)
        if not part.endswith(SEPARATOR):
            part = part + SEPARATOR
        line = part + ' '
        counter = 1
    logging.debug('[DEBUG appendLine: counter: {} ]'.format(counter))
    return line, counter, lines

def extractValueFromIndexes(line, header, header_indexes):
    """
    """ 
    resulting_line = ''
    _starting_index = 0
    #_new_line = False

    if any([line.count(value) for value in Constants.OUTPUT_ENDING.value]):
        return line

    for m, _line_element in enumerate(line.split()):
        _index = header_indexes[m]
        ##_index = header_indexes[m] if header_indexes[m]>0 else 0
        ##_index = header_indexes[m] if m>0 else 0

        inline_index = line[_starting_index:].index(_line_element)
        # try:
        #     inline_index = line[_starting_index:].index(_line_element)
        # except ValueError:
        #     print(_starting_index, _line_element)

        _cdt_0 = inline_index + len(_line_element) == len(header[m]) + _index # CASE: 1st element (hence column label is right-aligned) but the length of the element value is larger then the column label, hence the value will start before the column value. CONDITION: since the element value is also right-aligned, we compare that ' ... <VALUE>' end-index corresponds to the ' ..... <COLUMN_LABEL>' end-index.
        _cdt_1 = inline_index == _index - _starting_index # CASE: since the line[_starting_index:] should now starts with a space (the one that separates the element values), the next element value should be found at inline_index 1. CONDITION: we check that _index - _starting_index == 1
        _cdt_2 = inline_index == (_index-1) + len(header[m]) - _starting_index
        if any([_cdt_0, _cdt_1, _cdt_2]):
            resulting_line += _line_element + SEPARATOR
            #_starting_index += _index if _cdt_1 else (_index) + len(_line_element[m])
            #_starting_index = _index + max(len(_line_element), len(header[m]))
        elif inline_index in header_indexes:
            resulting_line += (header_indexes.index(inline_index) - m) * (EMPTY_FIELD + SEPARATOR) + _line_element + SEPARATOR
        else:
            resulting_line += EMPTY_FIELD + SEPARATOR
            #_starting_index = len(header[m]) + header_indexes[m]

        ##_starting_index = _index + max(len(_line_element), len(header[m]))
        if m==0 and len(header[m])>len(_line_element):
            _starting_index = _index + len(header[m])
        elif m==0:
            _starting_index = len(_line_element)
        else:
            _starting_index = _index + max(len(_line_element), len(header[m]))

    if resulting_line.count(SEPARATOR) < len(header):
        resulting_line += (len(header)-resulting_line.count(SEPARATOR))*(EMPTY_FIELD + SEPARATOR)

    return resulting_line

def extractor(content, n_field=None, debug=False, **kwargs):
    """
    Extract the SQLPLUS result in human readable way. The main goal is to get 
    rid of the several occurences of the field names that make the output 
    absolutely cumbersome to read. Just useless without reformatting. 
    
    Parameters
    ----------
    content: list
        List of string, one item for each lines read in the output file generated 
        by the SQLPLUS run.
    
    content: str
        A single string that encapsulates each lines read in the output file generated 
        by the SQLPLUS run, all separated with '\n'.        
    """
    if isinstance(content, str):
        content = [_c for _c in content.split('\n') if len(_c)>0]
    elif isinstance(content, list):
        content = [_c.replace('\n','') for _c in content if len(_c.replace('\n', ''))>0]
    else:
        assert False, 'content must be either a str or a list of str'

    cheader = []
    cropped_header = []
    lines = []
    J = -1
    N = -1
    M = 0
    counter = 0
    _line = ''
    n_fromQuery = -1
    CHEADER_FOUND = False

    if not any([SEPARATOR in j for j in content]):
        add_separator = True
    else:
        add_separator = False

    for k, _c in enumerate(content):
        _c_modified = _c.replace(SEPARATOR, '').replace('    ', ' ').strip()
        if _c_modified.replace(' ', '-')=='-'*len(_c_modified) and (J==-1 or k==J+2) and not CHEADER_FOUND:
            cheader.append(content[k-1])
            cheader.append(content[k])
            J = k
            logging.debug('[DEBUG extractor: {} = {} ]'.format(k, _c))
        elif J>0 and k>=J+2 and not CHEADER_FOUND:
            CHEADER_FOUND = True
            cropped_header, cropped_header_dict, cropped_header_indexes = extractCroppedColumnNames(cheader, with_index=True)
            if n_field is None:
                n_field = len(cropped_header)

            assert len(cheader)%2==0, "Incoherent length of the cropped header"
            N = int(len(cheader)/2.)
            
            if add_separator:
                # FIXME
                if len(cropped_header_dict)>1:
                    var_header = cropped_header_dict[k-len(cheader)]
                    var_header_indixes = cropped_header_indexes[k-len(cheader)]
                else:
                    var_header = cropped_header_dict[0]
                    var_header_indixes = cropped_header_indexes[0]
                _c = extractValueFromIndexes(line=_c, header=var_header, header_indexes=var_header_indixes)
                _line = extractValueFromIndexes(line=content[k-1], header=cropped_header_dict[counter], header_indexes=cropped_header_indexes[counter])
            else:
                if not content[k-1].rstrip().endswith(SEPARATOR):
                    _line += content[k-1] + SEPARATOR
                else:
                    _line += content[k-1]

            counter += 1
            if _c in cheader:
                if M>2*N:
                    M = 0
                    _line += EMPTY_FIELD + SEPARATOR
                    counter += 1
                else:
                    M += 1
            else:
                _line, counter, lines = appendLine(_c, _line, lines, counter, N, n_field=n_field, debug=debug)
                
            #lines.append(content[k-1])
            logging.debug('[DEBUG extractor: {} = [FOUND] {} ]'.format(k, _c)) 
        elif CHEADER_FOUND:
            ##if _c in cheader:
            if _c.strip() in [_hline.strip() for _hline in cheader]:
                logging.debug('[DEBUG: k={} -- M={} -- 2N={} ]'.format(k, M, 2*N))
                if M>2*N:
                    M = 0
                    _line += EMPTY_FIELD + SEPARATOR
                    counter += 1
                else:
                    M += 1
            else:
                M = 0
                if add_separator:
                    _id = k-len(cheader)
                    if _id >= N:
                        _id = _id % N
                    _c = extractValueFromIndexes(line=_c, header=cropped_header_dict[_id], header_indexes=cropped_header_indexes[_id])
                else:
                    pass

                _line, counter, lines = appendLine(_c, _line, lines, counter, N, n_field=n_field, debug=debug)
                if kwargs and kwargs["QUERY_N_RESULT_RETURN"] in _c:
                    n_fromQuery = int(_c.split(kwargs["QUERY_N_RESULT_RETURN"])[0].replace(' ', ''))
                    break
                logging.debug('[DEBUG extractor: {} = {} ]'.format(k, _c))
        elif kwargs and isDBIssue(line=_c, errors=kwargs["DB_ERRORS"], warnings=kwargs["DB_WARNINGS"]):
            logging.error('DB error detected --> stop the processing')
            return None, None
        else:
            logging.debug('[DEBUG extractor: {} = [else] {} ]'.format(k, _c))
            continue
        
    lines += [_line]
    logging.debug('[DEBUG extractor: cheader length: {} ]'.format(len(cheader)))
    logging.debug('[DEBUG extractor: cheader.......: {} ]'.format(cheader))
    logging.debug('[DEBUG extractor: lines length..: {} ]'.format(len(lines)))
    logging.debug('[DEBUG extractor: n query.......: {} ]'.format(n_fromQuery))

    return lines, cropped_header

def generateOutputFileHeader(table=None, query=None):
    """
    Generate a header for the output file. 
    """
    header = "QUERY\n-----\n{q}\n\n\nRESULT\n------\n\n"
    if table is None and query is None:
        return ''
    elif table is not None and query is None:
        return header.format(q="SELECT * FROM {t};".format(t=table.upper()))
    elif query is not None:
        return header.format(q=query.upper())
    else:
        return ''

def get_max_length(mylist, reference=None):
    """
    Given a list of strings 'mylist' and a list of lengths (int) 'reference', 
    the function returns an updated version of 'reference' where only the 
    max length between the str and the reference is kept. 
    
    This aims at to be used to format the output file with each column has the 
    size defined wrt to the larger content it includes.
    
    Parameters
    ----------
    mylist: list of str
        For example, mylist = ['data 1', 'tested A', ...]
    
    reference: list of int (or None)
        For example: reference = [2, 13, ...]
        
    With the examples given above, the result would be: [6, 13] since:
    a) len('data 1') == 6 > 2 --> we update to 6
    b) len('tested A') == 8 <= 13 --> we keep 13
    """
    if reference is None:
        return [len(_v) for _v in mylist]

    assert len(mylist)==len(reference), "The list (size={}) and the list-reference (size={}) must have the same size.".format(len(mylist), len(reference))
    return [len(value) if len(value)>b else b for value, b in zip(mylist, reference)]

def formatter(content, header=None, output_header=None ,debug=False, **kwargs):
    """
    Format in a readable way the line extracted with the function extractor(),
    then write the result in an output file.
    
    Parameters
    ----------
    content: list
    """
    if content is None:
        return None

    if output_header is None:
        output_header = ''
    else:
        if not output_header.endswith('\n'):
            output_header += '\n'

    for j, r in enumerate(content):
        logging.debug('[DEBUG formatter: j --> r: {} --> {} ]'.format(j, r))

    if header is not None:
        header_lengths = [len(_h) for _h in header]
        data_length_max = [_v for _v in header_lengths]
    else:
        #header_lengths = [0]
        data_length_max = None

    logging.debug('[DEBUG formatter: header: {} ]'.format(header))
    logging.debug('[DEBUG formatter: data_length_max: {} ]'.format(data_length_max))

    result = ''
    result += output_header

    #for _h in header:
    #    result += '{h:{l}}'.format(h=_h, l=len(_h)+3)

    content_cleaned = []
    for k, _line in enumerate(content):
        logging.debug('[DEBUG formatter: _line: {} ]'.format(_line))
        
        if _line.rstrip().endswith(SEPARATOR):
            _line = _line.rstrip()[:-len(SEPARATOR)]
        _temp = [_v.strip() if len(_v.strip())>0 else EMPTY_FIELD for _v in _line.split(SEPARATOR)]
        logging.debug('[DEBUG formatter: _temp: {} ]'.format(_temp))
        if data_length_max is None:
            data_length_max = [len(_v) for _v in _temp]
        else:
            data_length_max = get_max_length(_temp, data_length_max)
        content_cleaned.append(_temp)

    _separator = ''
    if header is None:
        header = [''] * len(data_length_max)
        
    for k, (_h, _l) in enumerate(zip(header, data_length_max)): # Create the header of the output file
        ##result += '{value:>{length}}  '.format(length=_l, value=_h)
        result += "{value}".format(value=_h.ljust(_l)) + 2*" "
        _separator += '-'*_l + 2*" "
    result += '\n' + _separator + '\n'

    for k, _line in enumerate(content_cleaned):
        for k, (_field, _l) in enumerate(zip(_line, data_length_max)):
            result += '{value:>{length}}  '.format(length=_l, value=_field)
        result += '\n'

    if kwargs:
        writeOutputFile(result, root_output_file=kwargs["ROOT_OUTPUT_FILE"])
    else:
        return result

class MyParser:
    """
    """
    def __init__(self, 
        verbose=False, 
        debug=False, 
        generateDBSchemeInformation=False, 
        inputFile=False, 
        select=False, 
        table=False,
        logLevel="INFO",
        columns=False,
        ):
        """
        """
        self.verbose = verbose
        self.debug = debug
        self.generateDBSchemeInformation = generateDBSchemeInformation
        self.inputFile = inputFile
        self.select = select
        self.table = table
        self.logLevel = logLevel
        self.columns = columns

def define_argparse():
    """
    """
    _help = {
            'verbose': """Activate the verbose mode.""",
            'debug': """Activate the debug mode.""",
            'inputFile': """Format the output of an SQLPLUS run, contained in the given filename.""",
            'generateDBSchemeInformation': """Generate several output files that contain information about the database scheme""",
            'select':"""Run the simple 'select'-type SQL query""",
            'columns':"""Get the names of the columns for the given table""",
            'table':"""Run a 'select'-type SQL query over all fields for the given table""",
            'logLevel':"""Define the log level for loggin, between DEBUG, INFO, WARNING, ERROR, and CRITICAL""",
    }
    _description = """"""
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument('-v', '--verbose', action='store_true', help=_help['verbose'])
    parser.add_argument('-d', '--debug', action='store_true', help=_help['debug'])
    parser.add_argument('-g', '--generateDBSchemeInformation',  action='store_true', help=_help['generateDBSchemeInformation'], default=False)

    parser.add_argument('-i', '--inputFile', help=_help['inputFile'], default=False)
    parser.add_argument('-s', '--select', help=_help['select'])
    parser.add_argument('-t', '--table', help=_help['table'])
    parser.add_argument('-l', '--logLevel', help=_help['logLevel'], default="INFO")
    parser.add_argument('-c', '--columns', help=_help['columns']) 
    return parser

def mainFromServer(sqlplus_input=None):
    """Backend function called from Server side -- flask"""
    if sqlplus_input is None:
        return ''
    elif sqlplus_input.strip() == '':
        return 'Empty input'
    result, cropped_header = extractor(sqlplus_input, n_field=None, debug=False)
    sql_result = formatter(result, header=cropped_header, debug=False)
    return sql_result

# MAIN
def main(args=None, inputFromServer=None):
    """
    """
    DEBUG_MODE = False
    if args is None:
        parser = define_argparse()
        args = parser.parse_args()
    else:
        args = args


    if args.verbose:
        VERBOSE_MODE = True
    else:
        VERBOSE_MODE = False

    if args.debug:
        DEBUG_MODE = True
    else:
        DEBUG_MODE = False
        
    if args.inputFile:
        formatter_only = True
        inputFilename = args.inputFile
    else:
        formatter_only = False
        inputFilename = None

    if args.generateDBSchemeInformation:
        generateDBSchemeInformation = True
    else:
        generateDBSchemeInformation = False

    if args.select:
        myselect = args.select
    else:  
        myselect = None

    if args.table:
        mytable = args.table
    else:
        mytable = None

    if args.columns:
        columns_only = True
        columns_table = args.columns
    else:
        columns_only = False
        columns_table = None

    # LOGGING CONFIGURATION
    if args.logLevel:
        log_level = getattr(logging, args.logLevel.upper())
    logging.basicConfig(level=log_level, filename="recon_SQLPLUS_tool.log", filemode="w",
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # logging.debug("debug")
    # logging.info("info")
    # logging.warning("warning")
    # logging.error("error")
    # logging.critical("critical")

    DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    config = readConfigFile(DIR_PATH)
    SQL_FILE = config.get('SQL_FILE', None)
    ROOT_PATH = config.get('ROOT_PATH', None)
    INPUT_FILE_REPOSITORY = os.path.join(ROOT_PATH, config.get('INPUT_FILE_REPOSITORY', None))
    OUTPUT_FILE_REPOSITORY = os.path.join(ROOT_PATH, config.get('OUTPUT_FILE_REPOSITORY', None))
    ENV_CONFIG = '{usr}/{pwd}@{env}'.format(
        usr=config.get('ENV_CONFIG_USR', ''), 
        pwd=config.get('ENV_CONFIG_PWD', ''), 
        env=config.get('ENV_CONFIG_ENV', '')
        )
    SQL_TEMP_PATH_FILENAME = generateValidFormatedPath(os.path.join(ROOT_PATH, config.get('INPUT_FILE_REPOSITORY', None), SQL_TEMP_FILENAME))
    
    ROOT_SQL_FILE = os.path.join(ROOT_PATH, config.get('INPUT_FILE_REPOSITORY', None), SQL_FILE) 
    
    SQL_TEMP_FILE = 'echo exit | sqlplus -s {env} @{sqlFile}'.format(env=ENV_CONFIG, sqlFile=SQL_TEMP_PATH_FILENAME)
    
    N_MAX_LINE_PER_OUTPUTFILE = int(config['N_MAX_LINE_PER_OUTPUTFILE'])
    config_language = defineLanguageSpecificConfig(config['LANGUAGE'])
    QUERY_N_RESULT_RETURN = config_language['QUERY_N_RESULT_RETURN']
    DB_ERRORS = [_k for _k in DB_ISSUES['ERROR'].keys()]
    DB_WARNINGS = [_k for _k in DB_ISSUES['WARNING'].keys()]

    config_kwargs = {
        "DB_ERRORS": DB_ERRORS,
        "DB_WARNINGS": DB_WARNINGS,
        "QUERY_N_RESULT_RETURN": QUERY_N_RESULT_RETURN,
    }

    OUTPUT_HEADER = ''
    
    if generateDBSchemeInformation:
        #
        #
        #
        OUTPUT_FILES = {
            "get_all_user_tables": "user_tables.out",
            "get_all_notempty_user_tables": "user_tables_not_empty.out",
        }
        ROOTS = {_key: generateValidFormatedPath(os.path.join(OUTPUT_FILE_REPOSITORY, _value)) for _key, _value in OUTPUT_FILES.items()}

        for _key, _root in ROOTS.items():
            _query = QUERIES[_key]
            config_kwargs["ROOT_OUTPUT_FILE"] = _root
            OUTPUT_HEADER = generateOutputFileHeader(query=_query)
            # _result, _e = runSQLquery(
            #     _query,
            #     env_config=ENV_CONFIG,
            #     db_err=DB_ISSUES['ERROR']['no result'][config['LANGUAGE']]
            # )
            query_elements = extractInfoFromSelectQuery(_query)
            columns = query_elements.get("fields", False)   
            generateSQLfile(query=_query, sql_temp_path_filename=SQL_TEMP_PATH_FILENAME)
            _res, _err = runSQLcommand(SQL_TEMP_FILE)
            if _err is None:
                result, cropped_header = extractor(_res, n_field=len(columns), debug=DEBUG_MODE, **config_kwargs)
                if result is not None:
                    sql_result = formatter(result, header=columns, output_header=OUTPUT_HEADER, debug=DEBUG_MODE, **config_kwargs)
            else:
                logging.error(_err)                    

    elif formatter_only and not generateDBSchemeInformation and myselect is None:
        # Format an input file containing SQLPLUS content
        #
        #
        logging.debug('MODE ...........: processing an input file')
        OUTPUT_FILE = inputFilename.replace('.', '_formated.')
        ROOT_OUTPUT_FILE = generateValidFormatedPath(os.path.join(OUTPUT_FILE_REPOSITORY, OUTPUT_FILE))
        config_kwargs["ROOT_OUTPUT_FILE"] = ROOT_OUTPUT_FILE
        logging.debug(f'OUTPUT_FILE ....: {OUTPUT_FILE}')
        logging.debug(f'ROOT_OUTPUT_FILE: {ROOT_OUTPUT_FILE}')
        if inputFromServer:
            _res = inputFromServer
        else:
            _res = readFile(inputFilename, root=INPUT_FILE_REPOSITORY)
        result, cropped_header = extractor(_res, n_field=None, debug=DEBUG_MODE, **config_kwargs)
        if result is not None:
            sql_result = formatter(result, header=cropped_header, debug=DEBUG_MODE, **config_kwargs)
            logging.info('DONE')

    elif columns_only and not generateDBSchemeInformation and myselect is None:
        _columns, _e = runSQLquery(
            QUERIES['get_column_names'].format(columns_table), 
            env_config=ENV_CONFIG, 
            db_err=DB_ISSUES['ERROR']['no result'][config['LANGUAGE']]
            )
        assert _e is None, "\nInitial query: {i}\nQuery........: {q}\nResult.......: {r}".format(
            i=line.replace('\n', ''),
            q=QUERIES['get_column_names'].format(_table),
            r=_e
            )
        columns = _columns = extractColumnNames(_columns.split('\n'))
        for k, _c in enumerate(columns, start=1):
            print(f"{k:3}: {_c}")

    else:
        # Open the SQL_FILE and extract the first valid SELECT SQL query
        # Extract the table name, then extract the headers by running the QUERIES['get_column_names']
        # Generate the temporarily SQL file with additional options, then run it
        # Run the 'extractor()', then the 'formatter()' functions
        # Delete the temporarily SQL file

        if myselect is not None:
            OUTPUT_FILE = 'specific_select.out'
            ROOT_OUTPUT_FILE = generateValidFormatedPath(OUTPUT_FILE_REPOSITORY)#os.path.join(ROOT_PATH, OUTPUT_FILE))
            config_kwargs["ROOT_OUTPUT_FILE"] = ROOT_OUTPUT_FILE                  
            line = myselect
            OUTPUT_HEADER = generateOutputFileHeader(query=myselect)
            logging.info('Run the SQL query: {}'.format(line))

        elif mytable is not None:
            OUTPUT_FILE = '{}.out'.format(mytable)
            ROOT_OUTPUT_FILE = generateValidFormatedPath(OUTPUT_FILE_REPOSITORY)#os.path.join(ROOT_PATH, OUTPUT_FILE))
            config_kwargs["ROOT_OUTPUT_FILE"] = ROOT_OUTPUT_FILE                  
            line = 'select * from {};'.format(mytable)
            OUTPUT_HEADER = generateOutputFileHeader(table=mytable)
            logging.info('Run the SQL query: {}'.format(line))

        else:
            OUTPUT_FILE = SQL_FILE.replace('.sql', '.out')
            ROOT_OUTPUT_FILE = generateValidFormatedPath(OUTPUT_FILE_REPOSITORY)#os.path.join(ROOT_PATH, OUTPUT_FILE))
            config_kwargs["ROOT_OUTPUT_FILE"] = ROOT_OUTPUT_FILE            
            with open(ROOT_SQL_FILE.replace('\'', ''), 'r') as f:
                for k, line in enumerate(f.readlines(), start=1):
                    if line.lower().startswith(SELECT):
                        logging.info('Run the SQL query: {}'.format(line))
                        OUTPUT_HEADER = generateOutputFileHeader(query=line)
                        break #Only the first valid uncommeted SELECT query is considered.
                    else:
                        pass
                    
        result_getCount = getCount(line, ENV_CONFIG)
        if result_getCount > N_MAX_LINE_PER_OUTPUTFILE:
            valid_while_output = False
            while not valid_while_output:
                wanna_continue = input(f"The SQL query will return {result_getCount} rows (> N_MAX_LINE_PER_OUTPUTFILE = {N_MAX_LINE_PER_OUTPUTFILE}). Do you want to continue anyway? [Y/n] ")
                if wanna_continue == "Y":
                    valid_while_output = True
                elif wanna_continue == 'n':
                    print("Process ABORTED")
                    return None
                else:
                    continue

        query_elements = extractInfoFromSelectQuery(line)
        _table = query_elements.get("table_name", getTableName(line))
        _columns = query_elements.get("fields", False)
        if not _columns:
            _header, _e = runSQLquery(
                QUERIES['get_column_names'].format(_table), 
                env_config=ENV_CONFIG, 
                db_err=DB_ISSUES['ERROR']['no result'][config['LANGUAGE']]
                )
            assert _e is None, "\nInitial query: {i}\nQuery........: {q}\nResult.......: {r}".format(
                i=line.replace('\n', ''),
                q=QUERIES['get_column_names'].format(_table),
                r=_e
                )
            
            _columns = extractColumnNames(_header.split('\n'))
            logging.debug('[DEBUG: _header: {} ]'.format(_header))
            logging.debug('[DEBUG: _columns: {} ]'.format(_columns))
            logging.debug('[DEBUG: _table: {} ]'.format(_table))
        else:
            logging.debug('[DEBUG: _columns: {} ]'.format(_columns))
            logging.debug('[DEBUG: _table: {} ]'.format(_table))
        W = len(_columns)
        generateSQLfile(query=line, sql_temp_path_filename=SQL_TEMP_PATH_FILENAME)
        _res, _err = runSQLcommand(SQL_TEMP_FILE)
        logging.debug('[DEBUG: _res runSQLcommand: -->\n')
        logging.debug(f"{_res}")
        logging.debug('<-- ]')
        if _err is None:
            result, cropped_header = extractor(_res, n_field=W, debug=DEBUG_MODE, **config_kwargs)
            if result is not None:
                sql_result = formatter(result, header=_columns, output_header=OUTPUT_HEADER, debug=DEBUG_MODE, **config_kwargs)
        else:
            logging.error(_err)

    if os.path.exists(SQL_TEMP_PATH_FILENAME.replace('\'', '')):
        os.remove(SQL_TEMP_PATH_FILENAME.replace('\'', ''))
    logging.info('DONE')    

if __name__ == '__main__':
    myargs=None
    #myargs = MyParser(inputFile="sqlplus_02.txt") # --> FAILS: issue when a field value contains ' ' space(s)
    #myargs = MyParser(inputFile="VUNF_1701_input.txt") # --> works
    myargs = MyParser(inputFile="test_input.txt")
    ##main(args=myargs)


    sqlplus_input = """          REFREL USRMAJ      HEUDEB   STAANN DATCRT   SWIVAL_5 REGMAT      
---------------- ----------- -------- ------ -------- -------- ----------- 
VALIDT_2 VALIDT_1 REFNUM           SWIVAL_4 CODTIT     
-------- -------- ---------------- -------- -----------
A9I17UZNWQ4P2UJG YGMYMW2S7JU 05353811        20220108 00       FG4GJXB0LZJ 
01       899      A9J26IHNEQ9J7QXG 01       OOPJ75S4O8U 
A6A26GRYHS6X2ZZU STYIS91DAZ3 10571126 U      20180811 00       TQJUPC8V7YF 
53       874      C9D21BRBVV7T6SUY 01       7ONYFAXRTU4 
C4H13WESKV3X7TTW O9R8UQF5XV2 06202255        20170819 00       G7RAU0DTBHH 
95       791      B7L08DWJCT2I2JZU 01       A14GK9QJ52K 
A2G17VZIPR7D1JTI 7N9J0RIHG0X 02153949 U      20200326 00       KIZQYK93ERA 
18       255      C8J14ISIGE4I3KAC 00       SNQ4R5LOSDZ 
B6B02ICJZU3A5EQE PCDXN6MXZXK 08535733        20200911 01       FMW4D24YQO2 
41       756      B7K15MLOVK4Z7BYJ 01       WDRRBL3FJ99 
          REFREL USRMAJ      HEUDEB   STAANN DATCRT   SWIVAL_5 REGMAT      
---------------- ----------- -------- ------ -------- -------- ----------- 
VALIDT_2 VALIDT_1 REFNUM           SWIVAL_4 CODTIT     
-------- -------- ---------------- -------- -----------
A1C05ZFWJP4X5NIA 0ZY4FWDQMT6 02552255 U      20210125 01       F6K52X3I4NR 
09       420      B5H14HIOOL5Y6JAT 00       1UZKQOQB404 
B2G12JKCAS0P2AWN TDCJVAWK1YE 04344758        20200120 01       JS8LZWGYVRQ 
63       886      C8C02CUIID2E9NFN 00       QJY1RSMRD3T 
B4C16KPSGA9M8KFU BQ4G5SDWH07 24044009        20171226 01       78YGM48O3Q2 
85       838      B0A22UQMNM2F6HVK 01       2QEGF1CP156 
A5E21NRTLP5H0MJP BC5B8AYN28U 24003844        20181004 01       ZNIDRNUUUP3 
11       578      C8C25TMHQD8W1TWI 01       69O445F5KIQ 
A6E24FXYZP3K7AFJ ZQJ5SDVE7HU 09572628        20171011 00       XITWYJV1MK0 
00       207      C2H18STHIR6R0PBK 00       EM7MBX3G1YC 
          REFREL USRMAJ      HEUDEB   STAANN DATCRT   SWIVAL_5 REGMAT      
---------------- ----------- -------- ------ -------- -------- ----------- 
VALIDT_2 VALIDT_1 REFNUM           SWIVAL_4 CODTIT     
-------- -------- ---------------- -------- -----------
A8E12HFWEE3R1FAH 91M8HM0643X 22155100 U      20170326 01       DS86UXXGH45 
43       174      A2K13NCSNH5A5MQX 00       H55DXICIPJS 
B3J09FNDDB3L0LIX VIU7ARIKVL2 06561245        20170515 01       KWHL3EZ8NE3 
97       231      B6D25DFKCA8A7DGY 00       L8AGQOJ5616 
A8H16OQWFP5C6LAF JRIY565VZX4 00544842        20181207 01       L50K7DB1VPU 
41       183      C4J04JGRRZ4B5SAM 01       T5P0XTL8GX9 
B6E13ZZWYP2X8GSH 7AM16E42LOS 07282233 U      20190103 00       PM5Y2F8GP7A 
45       795      B8E08BXUHR2F3SYX 00       048EMWIE3YB 
A4B27YTXPK1G3KRA 9K5E1U74PRJ 09134138        20220516 01       CNYK3SVX87G 
40       678      C2I27JHIEU9D7MXG 01       NOG1GDC05F2 
          REFREL USRMAJ      HEUDEB   STAANN DATCRT   SWIVAL_5 REGMAT      
---------------- ----------- -------- ------ -------- -------- ----------- 
VALIDT_2 VALIDT_1 REFNUM           SWIVAL_4 CODTIT     
-------- -------- ---------------- -------- -----------
A9D10BURQT6J7OKN FN6CLBVXSAE 06333516        20200324 00       DACX2OQB9UV 
81       231      B5D28WMGWZ7P7YKR 01       ZL7DEP0ZC3D 
A2A10AMLDW2N6EWB WLZ93FM0MUZ 01151609 U      20170404 01       2Q60A1GFWZB 
74       830      C0A15MJRMN4I9FYO 00       TD5CYCK2DT4 
C3I19LGUUE0U1OZL FAA6M0BHBEM 08454845        20170128 00       0605FMXU44G 
20       457      B8F28UEGDH4N3WVE 01       LXJTK3W1KOY 
A2G09IFXCX5R6YQQ W0JAK17B8ZN 20502318        20210105 00       L1Q2THG25Y7 
10       711      C1C03VXWQS7H5DMU 01       Q6SKT8ZYFVU 
B5H06ONOXJ3D7FRD HTJS49AMSL0 06164257        20210608 00       HZMYGQEKNST 
67       476      A6D19TWZAR5D9YVY 00       YTUWOVO6HOF 
"""
    print(mainFromServer(sqlplus_input=sqlplus_input))
