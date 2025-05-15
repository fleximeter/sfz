"""
File: main.py

This file runs the parser.
"""

import lexer
import parser

if __name__ == "__main__":
    FILE = "sample_files/Northern Trumpets_BreathContr_1.1.sfz"
    with open(FILE, 'r') as sfz_file:
        contents = sfz_file.read()
    lex = lexer.Lexer(contents)
    # for i in range(200):
    #     print(f"{lex.tokenized_buffer[i].token_type} \"{lex.tokenized_buffer[i].lexeme}\"")
    data = parser.parse(lex.tokenized_buffer)
    for i in range(50, 55):
        print(data[i].header)
        print(data[i].attributes)
        print()
    