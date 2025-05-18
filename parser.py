"""
File: parser.py

This file turns a lexed buffer into something more manageable.
"""

from lexer import SfzSyntaxError, TokenType, Lexer
import sfztypes

class Parser:
    def __init__(self, lexer: Lexer):
        """
        Initializes the parser and parses the tokenized buffer in the lexer
        :param lexer: The lexer containing the tokenized buffer
        """
        self.lexer = lexer
        self.parsed_buf = self.parse()

    def parse(self) -> list:
        """
        A simple parser for a tokenized buffer
        """
        parsed_buf = []
        current_header = None
        for i, token in enumerate(self.lexer.tokenized_buffer):
            if token.token_type == TokenType.HEADER:
                if current_header is not None:
                    parsed_buf.append(current_header)
                if token.lexeme == "<region>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.REGION)
                elif token.lexeme == "<group>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.GROUP)
                elif token.lexeme == "<control>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.CONTROL)
                elif token.lexeme == "<global>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.GLOBAL)
                elif token.lexeme == "<curve>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.CURVE)
                elif token.lexeme == "<effect>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.EFFECT)
                elif token.lexeme == "<master>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.MASTER)
                elif token.lexeme == "<midi>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.MIDI)
                elif token.lexeme == "<sample>":
                    current_header = sfztypes.Header(sfztypes.OpCodeHeader.SAMPLE)
                else:
                    raise SfzSyntaxError(f"Bad header token \"{token.lexeme}\" at line {token.line}, column {token.column}.")
            elif token.token_type == TokenType.KEY:
                # A key must be followed by =
                if i + 2 >= len(self.lexer.tokenized_buffer):
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                elif self.lexer.tokenized_buffer[i+1].token_type != TokenType.OPERATOR:
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
            elif token.token_type == TokenType.OPERATOR:
                if i == 0:
                    raise SfzSyntaxError(f"Floating operator = at line {token.line}, column {token.column}.")
                # The next token after an = must be a value
                elif self.lexer.tokenized_buffer[i+1].token_type != TokenType.INT_VALUE and \
                    self.lexer.tokenized_buffer[i+1].token_type != TokenType.FLOAT_VALUE and \
                    self.lexer.tokenized_buffer[i+1].token_type != TokenType.STRING_VALUE:
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
            elif token.token_type == TokenType.INT_VALUE or token.token_type == TokenType.FLOAT_VALUE or token.token_type == TokenType.STRING_VALUE:
                if i < 1:
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                # Sometimes a STRING_VALUE is an include path
                elif i == 1:
                    if self.lexer.tokenized_buffer[i-1].token_type != TokenType.INCLUDE or token.token_type != TokenType.STRING_VALUE:
                        raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                    else:
                        parsed_buf.append(sfztypes.Include(token.lexeme, self.source_file_path))

                # Values must always be preceded by =
                elif self.lexer.tokenized_buffer[i-1].token_type != TokenType.OPERATOR and self.lexer.tokenized_buffer[i-1].token_type != TokenType.INCLUDE:
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                # If the syntax is correct, add the key/value pair.
                else:
                    current_header.add_attribute(self.lexer.tokenized_buffer[i-2].lexeme, token.lexeme)
        return parsed_buf
