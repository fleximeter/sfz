"""
File: converter.py

This file converts a SFZ file to a JSON file for use with programs like SuperCollider.
"""

import json
import jsonifier
import lexer
import os
import parser
import re
import sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            with open(sys.argv[1], 'r') as sfz_file:
                contents = sfz_file.read()
            lex = lexer.Lexer(contents)
            parse = parser.Parser(lex, sys.argv[1])
            sample_dict = jsonifier.make_sample_dictionary(parse)
            new_file = re.sub(r'\.sfz$', '', sys.argv[1], re.IGNORECASE) + ".json"
            with open(new_file, 'w') as json_file:
                json_file.write(json.dumps(sample_dict))
            print(f"Converted SFZ file \"{sys.argv[1]}\" to JSON: \"{new_file}\".")
        else:
            print(f"Error: The file \"{sys.argv[1]}\" cannot be found.")
    else:
        print("Usage:\npython converter.py filename_to_convert.sfz\nOutputs a JSON file with the same name in the same directory.")