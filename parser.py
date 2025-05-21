"""
File: parser.py

This file turns a lexed buffer into something more manageable.
"""

from lexer import SfzSyntaxError, TokenType, Lexer
import sfztypes

class Parser:
    def __init__(self, tokenized_buffer: list):
        """
        Initializes the parser and parses the tokenized buffer in the lexer
        :param tokenized_buffer: The tokenized buffer
        """
        self.tokenized_buffer = tokenized_buffer
        self.parsed_buf = self.parse()

    def parse(self) -> list:
        """
        A simple parser for a tokenized buffer
        """
        parsed_buf = []
        current_header = sfztypes.Header(sfztypes.OpCodeHeader.NO_HEADER)
        for i, token in enumerate(self.tokenized_buffer):
            if token.token_type == TokenType.HEADER:
                if current_header.header != sfztypes.OpCodeHeader.NO_HEADER or len(current_header.attributes) > 0:
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
                # Could it be a #define?
                if i > 0 and self.tokenized_buffer[i-1].token_type == TokenType.DEFINE:
                    if i+1 > len(self.tokenized_buffer) or \
                        (self.tokenized_buffer[i+1].token_type != TokenType.INT_VALUE and 
                         self.tokenized_buffer[i+1].token_type != TokenType.FLOAT_VALUE and 
                         self.tokenized_buffer[i+1].token_type != TokenType.STRING_VALUE):
                        raise SfzSyntaxError(f"A #define macro must be followed by a key and a value (at line {token.line}, column {token.column}).")
                # Otherwise, a key must be followed by =
                elif i + 2 >= len(self.tokenized_buffer):
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                elif self.tokenized_buffer[i+1].token_type != TokenType.OPERATOR:
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
            elif token.token_type == TokenType.OPERATOR:
                if i == 0:
                    raise SfzSyntaxError(f"Floating operator = at line {token.line}, column {token.column}.")
                # The next token after an = must be a value
                elif self.tokenized_buffer[i+1].token_type != TokenType.INT_VALUE and \
                    self.tokenized_buffer[i+1].token_type != TokenType.FLOAT_VALUE and \
                    self.tokenized_buffer[i+1].token_type != TokenType.STRING_VALUE:
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
            elif token.token_type == TokenType.INT_VALUE or token.token_type == TokenType.FLOAT_VALUE or token.token_type == TokenType.STRING_VALUE:
                # values must be preceded by something
                if i == 0:
                    raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                
                # Sometimes a STRING_VALUE is an include path or the key of a DEFINE binding
                elif i == 1:
                    if self.tokenized_buffer[i-1].token_type == TokenType.INCLUDE and token.token_type == TokenType.STRING_VALUE:
                        pass
                    else:
                        raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                else:
                    # if it's a #define, we just ignore it
                    if self.tokenized_buffer[i-2].token_type == TokenType.DEFINE and self.tokenized_buffer[i-1].token_type == TokenType.KEY:
                        pass
                    # Values must always be preceded by =
                    elif self.tokenized_buffer[i-1].token_type != TokenType.OPERATOR and self.tokenized_buffer[i-1].token_type != TokenType.INCLUDE:
                        raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
                    # If the syntax is correct, add the key/value pair.
                    else:
                        current_header.add_attribute(self.tokenized_buffer[i-2].lexeme, token.lexeme)
        return parsed_buf
