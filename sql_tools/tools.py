try:
    from  itertools import pairwise
except AttributeError:
    from more_itertools import pairwise
except ImportError:
    from more_itertools import pairwise
import os
import math
import re


#print("OWEOWE -- tools -- ", __name__)
if __name__ in ['sql_tools.tools', 'sql_tools.sql_tools.tools']:
    from .sql_query_configuration import Constants, SQLKeywords
else:
    from sql_query_configuration import Constants, SQLKeywords

# BASIC CONFIGURATION


# FUNCTIONS
def convertToBinary(num, length):
    """convert number to binary of N bits"""
    # Vector to store the number 
    bits = [0]*(length)
    if (num == 0):
        return bits
 
    i = length - 1
    while (num != 0):
        bits[i] = (num % 2)
        i -= 1
 
        # Integer division
        # gives quotient
        num = num // 2
 
    return bits
 
def getAllBinary(n):
    """Generate all N bit binary numbers"""
    binary_nos = []
 
    # Loop to generate the binary numbers
    for i in range(pow(2, n)):
        bits = convertToBinary(i, n)
        binary_nos.append(bits)
 
    return binary_nos

def generateAllCaseVersionOfAString(string: str, cap_lock=True) -> list:
    """General all the case sensitive version of a string"""
    string = string.strip()
    N = len(string)
    if cap_lock:
        N = min([N, 10]) # --> N=10 leads to 2**10 = 1024 possibilies

    result = (2**N) * ['']
    for k, combination in enumerate(getAllBinary(N)):
        result[k] = ''.join([character.upper() if case else character.lower() for (character, case) in zip(string, combination)])

    return result

def getCaseSignature(string: str):
    """Get the case signature of a string"""
    return [1 if character.isupper() else 0 for character in str]

def allIndex(substring: str, string: str, case_sensitive: bool = True):
    """Return the index of all occurences of a substring within a string"""
    substring = substring.replace('|', '\|')
    if case_sensitive:
        return [match.start() for match in re.finditer(substring, string)]
    else:
        # result = []
        # for substring in generateAllCaseVersionOfAString(substring):
        #     result += [match.start() for match in re.finditer(substring, string)]
        # return sorted(result)
        return [match.start() for match in re.finditer(substring.lower(), string.lower())]

def addHook(text: str, hook_type="SPACE") -> str:
    """Add a hook (replace a " " with a specific symbol) to ensure the string not to be stripped."""
    if hook_type == "SPACE":
        return text.replace(Constants.MONO_SPACE.value, Constants.HOOK_SPACE.value)
    elif hook_type == "QUERY_CLOSURE":
        return text.replace(Constants.QUERY_CLOSURE.value, Constants.HOOK_QUERY_CLOSURE.value)
    else:
        return text

def checkIfSubstringSurroundingIsSpaces(substring: str, position: int, string: str, to_compare=None) -> bool:
    """Check if the substring within the string is surrounded by spaces."""
    assert position>=0, "The `position` must be a positive integer"
    if to_compare is None:
        to_compare = [Constants.MONO_SPACE.value]
    elif Constants.MONO_SPACE.value not in to_compare:
        to_compare.append(Constants.MONO_SPACE.value)
    else:
        pass

    if position==0 and (position+len(substring))<(len(string)-2): # CASE: substring in position 0 and smaller than string
        if string[position+len(substring)] in to_compare:
            return True
        else:
            return False
    elif position>0 and (position+len(substring))<=(len(string)-2): # CASE: substring inside string and smaller than string
        if all([string[position-1] in to_compare, string[position+len(substring)] in to_compare]):
            return True
        else:
            return False
    elif position>0 and (position+len(substring))==len(string): # CASE: substring ends the string
        if string[position-1] in to_compare:
            return True
        else:
            return False
    else:
        return True

def isFunction(substring: str, position: str, string: str):
    """True if the substring is followed by '('."""
    for character in string[position+len(substring):]:
        if character == Constants.MONO_SPACE.value:
            continue
        elif character == Constants.PARENTHESIS_OPEN.value:
            return True
        else:
            return False
    return None

def replaceSpecificOccurencesOfSubstringInString(substring: str, positions: list, string: str) -> str:
    """Replace occurences substring in string for the given positions only"""
    new_string = ''
    _k = -1
    for k, letter in enumerate(string):
        if k in positions:
            new_string += letter.upper()
            _k = k + len(substring)
        elif k<_k:
            new_string += letter.upper()
        else:
            new_string += letter
    return new_string

def removeHook(text: str, hook_type="SPACE") -> str:
    """Remove the hook."""
    if hook_type == "SPACE":
        return text.replace(Constants.HOOK_SPACE.value, Constants.MONO_SPACE.value)
    elif hook_type == "QUERY_CLOSURE":
        return text.replace(Constants.HOOK_QUERY_CLOSURE.value, Constants.QUERY_CLOSURE.value)
    else:
        return text

def addSpaceAfterComma(text: str, hooked=True):
    """In a given string, add a space after a comma if not yet done"""
    if hooked: 
        sp = Constants.HOOK_SPACE.value
    else:
        sp = Constants.MONO_SPACE.value
    
    if sp not in text:
        return text

    return (Constants.SEPARATOR_COMMA.value + sp).join(text.split(Constants.SEPARATOR_COMMA.value))

def readConfigFile(config_file_path):
    """
    If it exists, it reads the config.py file and configures the 
    script before running it.
    
    Parameters
    ----------
    dir_path: str
        Absolute path of the repository from where the script is run.
    """
    config = {}
    with open(config_file_path, 'r') as f:
        for _line in f.readlines():
            if not _line.lstrip().startswith('#') and '=' in _line:
                split_line = _line.split('=')
                value = split_line[1].strip()
                if value.startswith('\'') and value.endswith('\''):
                    value = str(value[1:-1])
                config[split_line[0].strip()] = value
    return config

def configValidator(config, **kwargs):
    """Perform specific validation(s) of the config.ini content"""
    text = "Please modify the 'config.ini' using one of the following: "

    if config.get("LOG_LEVEL", False) and kwargs.get("VALID_LOG_LEVEL", False):
        assert config["LOG_LEVEL"].upper() in kwargs["VALID_LOG_LEVEL"], f"The log level '{config['LOG_LEVEL']}' is not recognized. {text}{kwargs['VALID_LOG_LEVEL']}"

    if config.get("KEYWORDS_CASE", False) and kwargs.get("VALID_KEYWORDS_CASE", False):
        assert config["KEYWORDS_CASE"] in kwargs["VALID_KEYWORDS_CASE"], f"The keyword case option '{config['KEYWORDS_CASE']}' is not recognized. {text}{kwargs['VALID_KEYWORDS_CASE']}"

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

def writeOutputFile(content, root_output_file):
    """
    If not yet existing, create the config.ini > 'OUTPUT_FILE' file and write the 
    'content' within it.

    Parameters
    ----------
    content: str
        A unique string written in the file 'ROOT_OUTPUT_FILE'.
    """
    os.umask(0)
    with open(root_output_file.replace('\'', ''), 'w+') as f:
    #with open(os.open(ROOT_OUTPUT_FILE.replace('\'', ''), os.O_CREAT | os.O_WRONLY, 0o777), 'w+') as f:
        f.write(content)
    return None

def checkIfPreviousEndswithNewlineTag(result: list) -> bool:
    """Check whether the last valid entry (not empty) from the result ends with \n"""
    for item in result[::-1]:
        if len(item):
            if item.rstrip(Constants.MONO_SPACE.value).endswith(Constants.NEW_LINE.value):
                return True
            else:
                return False
        else:
            continue
    return False

def removeNewlineTagOnLastEntry(result: list) -> list:
    """Remove the trailing \n from the last entry of the list"""
    result[-1] = result[-1].rstrip(Constants.NEW_LINE.value)
    return result

def removeTrailingSpacesOnLastEntry(result: list, k: int =None) -> list:
    """Remove the trailing \n from the last entry of the list"""
    if k is None:
        k = -1
    result[k] = result[k].rstrip(Constants.MONO_SPACE.value)
    return result

def appendSpacesOnLastEntry(result: list, n: int =1) -> list:
    """Append k spaces to the last entry of the list"""
    result[-1] = result[-1] + n * Constants.MONO_SPACE.value
    return result

def checkMultiQueryInFile(query: str):
    """
    Check whether there is more than one query in the input file. If so, split 
    into several queries. 

    FIXME: does not handle the case where ";" is included a string with other 
           text, e.g. "Test ; test" --> the ";" is not directly embedded by 
           simple/double quotes.
    FIXME: does not handle two or more consecutive ";" when stripped (e.g. 
           "Test ; ; test"). Might be solved by the previous FIXME
    """
    queries = {}

    query = query.strip()
    if query.count(Constants.QUERY_CLOSURE.value) <= 1:
        queries[0] = query

    else:
        indexes = allIndex(Constants.QUERY_CLOSURE.value, query)
        if indexes[0] > 0:
            indexes = [0] + indexes
        else:
            pass
        
        _query = ''
        j = 0
        for k, _pair in enumerate(pairwise(indexes)):
            _quotes = (Constants.SIMPLE_QUOTE.value, Constants.DOUBLE_QUOTE.value) 
            condition = all([query[:_pair[1]].strip()[-1] in _quotes, query[min((_pair[1]+1, len(query)-1)):].strip(Constants.MONO_SPACE.value)[0] in _quotes])
            if condition: #check that QUERY_CLOSURE is not in a string
                _query += query[_pair[0]:_pair[1]+1] if _pair[0]==0 else query[_pair[0]+1:_pair[1]+1]
                _query = addHook(_query, "QUERY_CLOSURE")
            else:
                queries[j] = f"{_query} {query[_pair[0]:_pair[1]+1] if _pair[0]==0 else query[_pair[0]+1:_pair[1]+1]}"
                _query = ''
                j += 1
    return queries

def forwardCheckIfInORBlock(string: str):
    """Check whether there is an OR in the same block"""
    level = 1
    for s in string:
        if Constants.PARENTHESIS_CLOSE.value in s:
            level -= 1
        elif Constants.PARENTHESIS_OPEN.value in s:
            level += 1

        if level == 0:
            return False
        elif level == 1 and s == "OR":
            return True
        else:
            continue
    return False

def testcase_re_sub_with_function():
    """Test Case for re.sub() with a function"""
    query = "select * from tab where tablename='a-b';"
    sep = "-"

    def foo(matchobj):
        print(matchobj.group())
        return f" {sep} "

    result = re.sub(f" *{sep} *", foo, query)
    return result


def sortSQLKeywords():
    """Display a sorted version of the SQL keywords."""
    for key in sorted(SQLKeywords.keywords.value):
        print(f"\"{key}\",")


def main():
    #print(generateAllCaseVersionOfAString('count '))
    #result = testcase_re_sub_with_function()
    #print(result)
    sortSQLKeywords()

if __name__ == '__main__':
    main()