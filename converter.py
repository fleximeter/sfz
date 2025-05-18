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

SFZ = re.compile(r"\.sfz$", re.IGNORECASE)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            with open(sys.argv[1], 'r') as sfz_file:
                contents = sfz_file.read()
            lex = lexer.Lexer(contents)
            parse = parser.Parser(lex)
            sample_dict = jsonifier.make_sample_dictionary(parse)
            new_file = re.sub(r'\.sfz$', '', sys.argv[1], re.IGNORECASE) + ".json"
            with open(new_file, 'w') as json_file:
                json_file.write(json.dumps(sample_dict))
            print(f"Converted SFZ file \"{sys.argv[1]}\" to JSON: \"{new_file}\".")
        else:
            print(f"Error: The file \"{sys.argv[1]}\" cannot be found.")

    elif len(sys.argv) == 3 and sys.argv[1] == '--dir':
        print(f"Converting directory {sys.argv[2]}...")
        if os.path.exists(sys.argv[2]):
            num_converted = 0
            for dir, _, files in os.walk(sys.argv[2]):
                for file in files:
                    if SFZ.search(file):
                        full_path = os.path.join(dir, file)
                        with open(full_path, 'r') as sfz_file:
                            contents = sfz_file.read()
                        lex = lexer.Lexer(contents)
                        parse = parser.Parser(lex)
                        sample_dict = jsonifier.make_sample_dictionary(parse)
                        new_file = re.sub(r'\.sfz$', '', full_path, re.IGNORECASE) + ".json"
                        with open(new_file, 'w') as json_file:
                            json_file.write(json.dumps(sample_dict))
                        print(f"Converted SFZ file \"{file}\" to JSON")
                        num_converted += 1
            print(f"Done. Converted {num_converted} files.")
                        
        else:
            print(f"Error: The directory \"{sys.argv[2]}\" cannot be found.")
    else:
        print("Usage:\n======\npython converter.py filename_to_convert.sfz\npython converter.py dir path_to_directory\n======\nOutputs a JSON file (or files) with the same name(s) in the same directory.")