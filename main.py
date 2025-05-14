"""
File: main.py

This file runs the parser.
"""

import lexer

if __name__ == "__main__":
    FILE = "sample_files/Northern Trumpets_BreathContr_1.1.sfz"
    with open(FILE, 'r') as sfz_file:
        contents = sfz_file.read()
    buf = lexer.lex_string(contents)
    print(buf[1].token_type)
    print(buf[1].lexeme)
    # for token in buf:
    #     print(token.token)
