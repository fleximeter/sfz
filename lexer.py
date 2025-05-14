"""
File: lexer.py

This file turns the SFZ file into a series of tokens.
"""

from enum import Enum

idx = 0
line = 0

class SfzSyntaxError(SyntaxError):
    def __init__(self, msg):
        super(SfzSyntaxError, self).__init__()
        self.msg = msg

class TokenType(Enum):
    COMMENT = 1 # comments start with //
    OPERATOR = 2 # generally just the = operator
    HEADER = 3 # an item inside <> brackets
    KEY = 4    # a key in a key/value pair
    STRING_VALUE = 5  # the string value in a key/value pair
    NUMBER_VALUE = 6  # the number value in a key/value pair
    BROKEN = 7 # for tokens that don't make any sense

# Tracks the state when we parse a key/value pair
class State(Enum):
    KEY = 1
    VALUE = 2
    OTHER = 3

class Token:
    def __init__(self, token_type: TokenType, text: str):
        self.token_type = token_type
        self.lexeme = text

def comment(string: str):
    """
    Lexes a comment
    :param string: The string that is being lexed
    :return: Returns the lexed token
    """
    global idx
    global line
    start_idx = idx
    while idx < len(string):
        if string[idx] == '\n':
            idx += 1
            break
        else:
            idx += 1
    return Token(TokenType.COMMENT, string[start_idx:idx-1])
    
def header(string: str):
    """
    Lexes a header
    :param string: The string that is being lexed
    :return: Returns the lexed token
    """
    global idx
    global line
    start_idx = idx
    while idx < len(string):
        if string[idx] == '>':
            idx += 1
            return Token(TokenType.HEADER, string[start_idx:idx])
        else:
            idx += 1
    raise SfzSyntaxError(f"Unexpected end of file at line {line} while parsing a header tag.")

def key(string: str):
    """
    Lexes a key in a key/value pair
    :param string: The string that is being lexed
    :return: Returns the lexed token
    """
    global idx
    global line
    start_idx = idx
    while idx < len(string):
        if string[idx] == ' ' or string[idx] == '=':
            return Token(TokenType.KEY, string[start_idx:idx])
        elif string[idx] == '\n':
            raise SfzSyntaxError(f"Unexpected newline at line {line} while parsing a key in a key/value pair.")
        else:
            idx += 1
    raise SfzSyntaxError(f"Unexpected end of file at line {line} while parsing a key in a key/value pair.")    

def operator(string: str):
    """
    Lexes an operator
    :param string: The string being lexed
    :return: Returns the lexed token
    """
    global idx
    idx += 1
    return Token(TokenType.OPERATOR, string[idx-1])

def val(string: str):
    """
    Lexes a value in a key/value pair
    :param string: The string that is being lexed
    :return: Returns the lexed token
    """
    global idx
    global line
    start_idx = idx
    while idx < len(string):
        if string[idx] == ' ' or string[idx] == '\n':
            return Token(TokenType.KEY, string[start_idx:idx])
        elif string[idx] == '=':
            raise SfzSyntaxError(f"Unexpected operator '=' at line {line} while parsing a value in a key/value pair.")
        else:
            idx += 1
    return Token(TokenType.STRING_VALUE, string[start_idx:idx])    

def lex_string(string: str):
    """
    Lexes a provided string and returns a tokenized buffer
    :param string: The string to lex
    :return: A tokenized buffer
    """
    global idx
    global line
    tokenized_buf = []
    state = State.OTHER

    idx = 0
    line = 0

    while idx < len(string):
        if string[idx] == '\n':
            state = State.OTHER
            line += 1
            idx += 1
        if string[idx] == '<':
            state = State.OTHER
            tokenized_buf.append(header(string))
        elif string[idx] == '/' and peek(string, '/'):
            state = State.OTHER
            tokenized_buf.append(comment(string))
        elif string[idx] == '=':
            state = State.VALUE
            tokenized_buf.append(operator(string))
        # we unconditionally advance for whitespace
        elif string[idx] == ' ':
            idx += 1
        elif state == State.OTHER:
            state = State.KEY
            tokenized_buf.append(key(string))
        elif state == State.VALUE:
            tokenized_buf.append(val(string))
            state = State.OTHER        
        # maybe we want to get rid of this eventually? is it a problem?
        else:
            idx += 1 

    return tokenized_buf

def peek(string: str, target: str) -> bool:
    """
    Looks at the next character in the string and checks if it's a match.
    :param string: The string being lexed
    :param target: The expected value of the next character
    :returns: True or False
    """
    global idx
    next_idx = idx + 1
    if next_idx >= len(string):
        return False
    elif string[next_idx] != target:
        return False
    else:
        return True
    