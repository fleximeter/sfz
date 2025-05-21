"""
File: lexer.py

This file turns the SFZ file into a series of tokens.
"""

from enum import Enum
from preprocessor import SourceFileFragment

class SfzSyntaxError(SyntaxError):
    """
    Represents a syntax error in a SFZ file
    """
    def __init__(self, msg):
        super(SfzSyntaxError, self).__init__()
        self.msg = msg

class TokenType(Enum):
    """
    Represents different kinds of tokens in a SFZ file
    """
    COMMENT = 1       # comments start with //
    INCLUDE = 2       # for including other SFZ files
    DEFINE = 3        # for #define bindings
    OPERATOR = 4      # generally just the = operator
    HEADER = 5        # an item inside <> brackets
    KEY = 6           # a key in a key/value pair
    STRING_VALUE = 7  # the string value in a key/value pair
    INT_VALUE = 8     # the number value in a key/value pair
    FLOAT_VALUE = 9   # the number value in a key/value pair
    BROKEN = 10       # for tokens that don't make any sense

# Tracks the state when we parse a key/value pair
class State(Enum):
    VALUE = 1
    EQ = 2

class Token:
    """
    Represents a single token in a SFZ file
    """
    def __init__(self, token_type: TokenType, contents, line: int, column: int, path: str):
        """
        Creates a new `Token`, given the contents, location, and `TokenType`.
        :param token_type: The `TokenType` of the token
        :param contents: The string representation of the token in the file
        :param line: The 1-based line number
        :param column: The 1-based column number
        :param path: The path of the file containing the token
        """
        self.token_type = token_type
        self.lexeme = contents
        self.line = line
        self.column = column
        self.path = path

class LineLexer:
    """
    A lexer for individual lines in a file. The `Lexer` class extracts lines
    and runs them through instances of this class.
    """
    def __init__(self, string: str, line_no: int, path=""):
        """
        Initializes the LineLexer with a provided line of text. Note that this lexer
        will stop lexing as soon as it notices a newline ('\n') and discard the
        rest of the string.
        :param string: The line of text
        :param line_no: The line number (used in error propagation)
        :param path: The path of the current SFZ file
        """
        self.string = string
        self.line_no = line_no
        self.idx = 0
        self.tokenized_buffer = []
        self.path = path
        self.lex()  # run the lexer
    
    def comment(self):
        """
        Lexes a comment
        """
        start_idx = self.idx
        while self.idx < len(self.string):
            if self.string[self.idx] == '\n':
                break
            else:
                self.idx += 1
        comment_str = self.string[start_idx:self.idx]
        self.idx = len(self.string)
        self.tokenized_buffer.append(Token(TokenType.COMMENT, comment_str, self.line_no + 1, start_idx + 1, self.path))
    
    def header(self):
        """
        Lexes a header token
        """
        start_idx = self.idx
        while self.idx < len(self.string):
            if self.string[self.idx] == '>':
                self.idx += 1
                self.tokenized_buffer.append(Token(TokenType.HEADER, self.string[start_idx:self.idx], self.line_no + 1, start_idx + 1, self.path))
                return
            self.idx += 1
        raise SfzSyntaxError(f"Unexpected end of line {self.line_no + 1} while parsing a header tag in file \"{self.path}\"")
    
    def key_value(self):
        """
        Lexes a key/value pair. This is annoyingly complicated because string values do not need to be enclosed in quotation marks.
        """
        block_start_point = self.idx

        # Track the start and end of the most recent word for key extraction
        word_start = self.idx
        word_end = -1

        state = State.VALUE

        while self.idx < len(self.string):
            if self.string[self.idx] == '/' and self.peek('/'):
                # If there's a trailing value, add it in
                self.value(self.string[block_start_point:self.idx], block_start_point)
                self.comment()
                return
            elif state == State.EQ:
                # Ignore all whitespace after an equals sign
                if not self.string[self.idx].isspace():
                    state = State.VALUE
                    word_start = self.idx
                    block_start_point = self.idx
            else:
                # If we hit an =
                if self.string[self.idx] == '=':
                    # If the string before the = has a separate word at the end, we pull out the beginning
                    # of the string and make it a value.
                    if block_start_point < word_start:
                        self.value(self.string[block_start_point:word_start-1], block_start_point)
                    # The word right before the = is the key.
                    self.tokenized_buffer.append(Token(TokenType.KEY, self.string[word_start:word_end], self.line_no + 1, word_start + 1, self.path))
                    state = State.EQ
                    self.tokenized_buffer.append(Token(TokenType.OPERATOR, self.string[self.idx], self.line_no + 1, self.idx + 1, self.path))
            
                # If a new word is starting, track that
                elif self.string[self.idx] == ' ' and self.peek_is_alpha():
                    word_start = self.idx + 1
                # If a word is ending, track that
                elif self.string[self.idx] != ' ' and (self.peek(' ') or self.peek('=')):
                    word_end = self.idx + 1    
            self.idx += 1
        
        # If there's a trailing value, add it in
        if block_start_point < self.idx:
            self.value(self.string[block_start_point:self.idx], block_start_point)

    def value(self, val: str, column: int):
        """
        Handles values (differentiates between strings and numbers)
        :param val: The value to handle
        """
        try:
            number = int(val)
            self.tokenized_buffer.append(Token(TokenType.INT_VALUE, number, self.line_no + 1, column + 1, self.path))
        except Exception as _:
            try:
                number = float(val)
                self.tokenized_buffer.append(Token(TokenType.FLOAT_VALUE, number, self.line_no + 1, column + 1, self.path))
            except Exception as _:
                self.tokenized_buffer.append(Token(TokenType.STRING_VALUE, val, self.line_no + 1, column + 1, self.path))

    def macro(self):
        """
        Manages macros
        """
        # Get the include macro
        start_idx = self.idx
        while self.idx < len(self.string):
            if self.string[self.idx] != ' ':
                self.idx += 1
            else:
                break
        macro_lexeme = self.string[start_idx:self.idx]

        # handle #include macros
        if macro_lexeme == "#include":
            self.tokenized_buffer.append(Token(TokenType.INCLUDE, macro_lexeme, self.line_no + 1, start_idx + 1, self.path))
            self.macro_include()

        # handle #define macros
        elif macro_lexeme == "#define":
            self.tokenized_buffer.append(Token(TokenType.DEFINE, macro_lexeme, self.line_no + 1, start_idx + 1, self.path))
            self.macro_define()

        else:
            raise SfzSyntaxError(f"Unrecognized macro \"{macro_lexeme}\" at line {self.line_no + 1}, column {start_idx + 1}, file \"{self.path}\"")

    def macro_define(self):
        """
        Manages lexing a define macro
        """
        idx = self.idx

        # Get the key
        start_key_idx = -1
        end_key_idx = -1
        while idx < len(self.string):
            if not self.string[idx].isspace():
                start_key_idx = idx
                idx += 1
                break
            else:
                idx += 1
        while idx < len(self.string):
            if self.string[idx].isspace():
                end_key_idx = idx
                break
            else:
                idx += 1
        key = self.string[start_key_idx:end_key_idx]
        if end_key_idx - start_key_idx < 2:
            raise SfzSyntaxError(f"Invalid #define key \"{key}\" at line {self.line_no + 1}, column {start_key_idx + 1}, file \"{self.path}\"")
        else:
            self.tokenized_buffer.append(Token(TokenType.KEY, key, self.line_no, start_key_idx, self.path))

        # Get the value
        start_val_idx = -1
        end_val_idx = -1
        while idx < len(self.string):
            if not self.string[idx].isspace():
                start_val_idx = idx
                idx += 1
                break
            else:
                idx += 1
        while idx < len(self.string):
            if self.string[idx].isspace():
                end_val_idx = idx
                idx += 1
                break
            else:
                idx += 1
        if end_val_idx == -1:
            end_val_idx = idx
        value = self.string[start_val_idx:end_val_idx]
        if end_val_idx - start_val_idx < 1:
            raise SfzSyntaxError(f"Invalid #define value \"{value}\" at line {self.line_no + 1}, column {start_key_idx + 1}, file \"{self.path}\"")
        self.value(value, start_val_idx)
        while idx < len(self.string):
            if not self.string[idx].isspace():
                raise SfzSyntaxError(f"Unexpected character \'{self.string[idx]}\' after #define key/value pair at line {self.line_no + 1}, column {start_key_idx + 1}, file \"{self.path}\"")
            idx += 1
        self.idx = idx
        
    def macro_include(self):
        """
        Manages lexing an include macro
        """
        # Get the trailing string
        while self.idx < len(self.string):
            if self.string[self.idx].isspace():
                self.idx += 1
            elif self.string[self.idx] == '\"':
                self.idx += 1
                break
            else:
                raise SfzSyntaxError(f"Missing include path after #include at line {self.line_no + 1}, column {self.idx + 1}, file \"{self.path}\"")
        
        start_str_idx = self.idx

        while self.idx < len(self.string):
            if self.string[self.idx] == '\"':
                include_path = self.string[start_str_idx:self.idx]
                self.tokenized_buffer.append(Token(TokenType.STRING_VALUE, include_path, self.line_no + 1, start_str_idx - 1, self.path))
                self.idx += 1
                return
            else:
                self.idx += 1

        raise SfzSyntaxError(f"Incorrectly formatted include path after #include at line {self.line_no + 1}, column {start_str_idx}, file \"{self.path}\"")

    def lex(self):
        """
        Manages the lexing process
        """
        while self.idx < len(self.string):
            if self.string[self.idx] == '/' and self.peek('/'):
                self.comment()
            elif self.string[self.idx] == '<':
                self.header()
            elif self.string[self.idx] == '#':
                self.macro()
            elif self.string[self.idx].isspace():
                self.idx += 1
            else:
                self.key_value()

    def peek(self, target: str) -> bool:
        """
        Looks at the next character in the string and checks if it's a match.
        :param string: The string being lexed
        :param target: The expected value of the next character
        :returns: True or False
        """
        next_idx = self.idx + 1
        if next_idx >= len(self.string):
            return False
        elif self.string[next_idx] != target:
            return False
        else:
            return True
        
    def peek_is_alpha(self) -> bool:
        """
        Checks if the next character is alphabetical
        """
        next_idx = self.idx + 1
        if next_idx >= len(self.string):
            return False
        elif not self.string[next_idx].isalpha():
            return False
        else:
            return True

    def peek_is_number(self) -> bool:
        """
        Checks if the next character is numeric
        """
        next_idx = self.idx + 1
        if next_idx >= len(self.string):
            return False
        elif not self.string[next_idx].isnumeric():
            return False
        else:
            return True


class Lexer:
    """
    Manages the lexing process for one string (typically, one file).
    The lexing happens automatically on construction, and the results are found
    in `self.tokenized_buffer`.
    """
    def __init__(self, frag: SourceFileFragment):
        """
        Creates a new `Lexer`.
        :param frag: The source file fragment to lex
        """
        self.string = frag.contents
        self.idx = 0
        self.line = frag.starting_line_number
        self.column = 0
        self.path = frag.path
        self.tokenized_buffer = []
        self.lex_string()
    
    def extract_line(self) -> str:
        """
        Extracts the next line from the string, advancing beyond the newline and discarding it/
        """
        start_idx = self.idx
        end_idx = start_idx
        while self.idx < len(self.string):
            # advance the position to the next line
            if self.string[self.idx] == '\n':
                self.idx += 1
                self.line += 1
                break
            else:
                self.idx += 1
                end_idx = self.idx
        return self.string[start_idx:end_idx]
        
    def lex_string(self):
        """
        Lexes a provided string and returns a tokenized buffer
        :param string: The string to lex
        :return: A tokenized buffer
        """
        self.idx = 0
        self.line = 0

        while self.idx < len(self.string):
            # We don't allow wrapping beyond the end of a line, so we just read in a line at a time.
            # This function also advances the index of the string buffer, so the while loop will end eventually.
            current_line = self.extract_line()

            # lex the current line and add its tokens
            line_lexer = LineLexer(current_line, self.line, self.path)
            self.tokenized_buffer += line_lexer.tokenized_buffer
