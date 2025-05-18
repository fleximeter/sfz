"""
File: tests.py

Contains tests to run on the SFZ code.
"""

import jsonifier
import lexer
import os
import parser
import re
import sfztypes

SFZ = re.compile(r"\.sfz$", re.IGNORECASE)
GREEN = "\033[92m"
END_COLOR = "\033[0m"

def test_batch_for_crashes(path):
    """
    Exhaustively tests all SFZ sample files in a directory
    :path: The directory to test
    """
    for dir, _, files in os.walk(path):
        for file in files:
            if SFZ.search(file):
                full_path = os.path.join(dir, file)
                # print(full_path)
                print("Testing", full_path)
                with open(full_path, 'r') as sfz_file:
                    contents = sfz_file.read()
                lex = lexer.Lexer(contents)
                parse = parser.Parser(lex)
                # Check that all include files can be accessed
                for item in parse.parsed_buf:
                    if type(item) == sfztypes.Include:
                        if not os.path.exists(item.full_path):
                            raise FileNotFoundError(f"The SFZ include file \"{item.path}\" in file \"{file}\" cannot be found.")
                        
                sample_groups = jsonifier.make_sample_dictionary(parse)
                # Check that all samples can be accessed
                for group in sample_groups:
                    for sample_arr in group:
                        for sample in sample_arr:
                            if "sample" in sample:
                                if not os.path.exists(os.path.join(parse.source_file_path, sample["sample"])):
                                   raise FileNotFoundError(f"The sample \"{sample['sample']}\" in file \"{file}\" cannot be found.")

if __name__ == "__main__":
    TEST_PATH = "D:\\Recording\\sfz"
    test_batch_for_crashes(TEST_PATH)
    print(GREEN + "All tests passed." + END_COLOR)
