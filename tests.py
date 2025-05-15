"""
File: tests.py

Contains tests to run on the SFZ code.
"""

import lexer
import parser
import os

def test_batch_for_crashes(path):
    for dir, _, files in os.walk(path):
        for file in files:
            print("Testing", os.path.join(dir, file))
            with open(os.path.join(dir, file), 'r') as sfz_file:
                contents = sfz_file.read()
            lexed = lexer.Lexer(contents)
            parsed = parser.parse(lexed.tokenized_buffer)

if __name__ == "__main__":
    test_batch_for_crashes("sample_files")
