"""
File: main.py

This file runs the parser.
"""

import jsonifier
import lexer
import parser

if __name__ == "__main__":
    FILE = "D:\\Recording\\sfz\\Northern Trumpets SFZ_1.1\\Northern Trumpets SFZ_1.1\\Northern Trumpets_BreathContr_1.1.sfz"
    with open(FILE, 'r') as sfz_file:
        contents = sfz_file.read()
    lex = lexer.Lexer(contents)
    parse = parser.Parser(lex, FILE)

    sample_groups = jsonifier.make_sample_dictionary(parse)
    for entry in sample_groups["Harmon Fast"][91]:
        print(entry)
        print()
    