"""
File: lexer.py

This file turns the SFZ file into a series of tokens.
"""

from enum import Enum

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
    OPERATOR = 3      # generally just the = operator
    HEADER = 4        # an item inside <> brackets
    KEY = 5           # a key in a key/value pair
    STRING_VALUE = 6  # the string value in a key/value pair
    INT_VALUE = 7     # the number value in a key/value pair
    FLOAT_VALUE = 8   # the number value in a key/value pair
    BROKEN = 9        # for tokens that don't make any sense

# Tracks the state when we parse a key/value pair
class State(Enum):
    VALUE = 1
    EQ = 2

class Token:
    """
    Represents a single token in a SFZ file
    """
    def __init__(self, token_type: TokenType, contents, line: int, column: int):
        """
        Creates a new `Token`, given the contents, location, and `TokenType`.
        :param token_type: The `TokenType` of the token
        :param contents: The string representation of the token in the file
        :param line: The 1-based line number
        :param column: The 1-based column number
        """
        self.token_type = token_type
        self.lexeme = contents
        self.line = line
        self.column = column

class LineLexer:
    """
    A lexer for individual lines in a file. The `Lexer` class extracts lines
    and runs them through instances of this class.
    """
    def __init__(self, string: str, line_no: int):
        """
        Initializes the LineLexer with a provided line of text. Note that this lexer
        will stop lexing as soon as it notices a newline ('\n') and discard the
        rest of the string.
        :param string: The line of text
        :param line_no: The line number (used in error propagation)
        """
        self.string = string
        self.line_no = line_no
        self.idx = 0
        self.tokenized_buffer = []
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
        self.tokenized_buffer.append(Token(TokenType.COMMENT, comment_str, self.line_no + 1, start_idx + 1))
    
    def header(self):
        """
        Lexes a header token
        """
        start_idx = self.idx
        while self.idx < len(self.string):
            if self.string[self.idx] == '>':
                self.idx += 1
                self.tokenized_buffer.append(Token(TokenType.HEADER, self.string[start_idx:self.idx], self.line_no + 1, start_idx + 1))
                return
            self.idx += 1
        raise SfzSyntaxError(f"Unexpected end of line {self.line_no + 1} while parsing a header tag.")
    
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
                if self.string[self.idx] != ' ':
                    state = State.VALUE
                    word_start = self.idx
                    block_start_point = self.idx
            else:
                # If a new word is starting, track that
                if self.string[self.idx] == ' ' and self.peek_is_alpha():
                    word_start = self.idx + 1
                # If a word is ending, track that
                elif (self.peek(' ') or self.peek('=')) and self.string[self.idx] != ' ':
                    word_end = self.idx + 1    
                # If we hit an =
                elif self.string[self.idx] == '=':
                    # If the string before the = has a separate word at the end, we pull out the beginning
                    # of the string and make it a value.
                    if block_start_point < word_start:
                        self.value(self.string[block_start_point:word_start-1], block_start_point)
                    # The word right before the = is the key.
                    self.tokenized_buffer.append(Token(TokenType.KEY, self.string[word_start:word_end], self.line_no + 1, word_start + 1))
                    state = State.EQ
                    self.tokenized_buffer.append(Token(TokenType.OPERATOR, self.string[self.idx], self.line_no + 1, self.idx + 1))
            
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
            self.tokenized_buffer.append(Token(TokenType.INT_VALUE, number, self.line_no + 1, column + 1))
        except Exception as _:
            try:
                number = float(val)
                self.tokenized_buffer.append(Token(TokenType.FLOAT_VALUE, number, self.line_no + 1, column + 1))
            except Exception as _:
                self.tokenized_buffer.append(Token(TokenType.STRING_VALUE, val, self.line_no + 1, column + 1))

    def include(self):
        """
        Manages include macros
        """
        # Get the include macro
        start_idx = self.idx
        while self.idx < len(self.string):
            if self.string[self.idx] != ' ':
                self.idx += 1
            else:
                break
        self.tokenized_buffer.append(Token(TokenType.INCLUDE, self.string[start_idx:self.idx], self.line_no + 1, start_idx + 1))

        # Get the trailing string
        while self.idx < len(self.string):
            if self.string[self.idx] == ' ':
                self.idx += 1
            elif self.string[self.idx] == '\"':
                self.idx += 1
                break
            else:
                raise SfzSyntaxError(f"Missing include path after #include at line {self.line_no + 1}, column {self.idx + 1}")
        
        start_str_idx = self.idx

        while self.idx < len(self.string):
            if self.string[self.idx] == '\"':
                self.tokenized_buffer.append(Token(TokenType.STRING_VALUE, self.string[start_str_idx:self.idx], self.line_no + 1, start_str_idx - 1))
                self.idx += 1
                return
            else:
                self.idx += 1

        raise SfzSyntaxError(f"Incorrectly formatted include path after #include at line {self.line_no + 1}, column {start_str_idx}")

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
                self.include()
            elif self.string[self.idx] == ' ':
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
    def __init__(self, string):
        """
        Creates a new `Lexer`.
        :param string: The contents of the file to lex
        """
        self.string = string
        self.idx = 0
        self.line = 0
        self.column = 0
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
            line_lexer = LineLexer(current_line, self.line)
            self.tokenized_buffer += line_lexer.tokenized_buffer
                