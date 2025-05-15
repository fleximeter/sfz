"""
File: parser.py

This file turns a lexed buffer into something more manageable.
"""

from enum import Enum
from lexer import SfzSyntaxError, TokenType
import sfztypes

def parse(tokenized_buffer: list) -> list:
    """
    A simple parser for a tokenized buffer
    """
    parsed_buf = []
    current_header = None
    for i, token in enumerate(tokenized_buffer):
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
            if i + 2 >= len(tokenized_buffer):
                raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
            elif tokenized_buffer[i+1].token_type != TokenType.OPERATOR:
                raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
        elif token.token_type == TokenType.OPERATOR:
            if i == 0:
                raise SfzSyntaxError(f"Floating operator = at line {token.line}, column {token.column}.")
            # The next token after an = must be a value
            elif tokenized_buffer[i+1].token_type != TokenType.INT_VALUE and \
                 tokenized_buffer[i+1].token_type != TokenType.FLOAT_VALUE and \
                 tokenized_buffer[i+1].token_type != TokenType.STRING_VALUE:
                raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
        elif token.token_type == TokenType.INT_VALUE or token.token_type == TokenType.FLOAT_VALUE or token.token_type == TokenType.STRING_VALUE:
            if i < 2:
                raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
            # Values must always be preceded by =
            elif tokenized_buffer[i-1].token_type != TokenType.OPERATOR:
                raise SfzSyntaxError(f"Bad key/value syntax at line {token.line}, column {token.column}.")
            # If the syntax is correct, add the key/value pair.
            else:
                current_header.add_attribute(tokenized_buffer[i-2].lexeme, token.lexeme)
    return parsed_buf
