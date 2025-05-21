"""
File: tests.py

Contains tests to run on the SFZ code.
"""

import jsonifier
import lexer
import os
import parser
import preprocessor
import re
import sfztypes

SFZ = re.compile(r"\.sfz$", re.IGNORECASE)
GREEN = "\033[92m"
END_COLOR = "\033[0m"

def test_dir_recursively(path):
    """
    Exhaustively tests all SFZ sample files in a directory
    :path: The directory to test
    """
    for dir, _, files in os.walk(path):
        for file in files:
            if SFZ.search(file):
                full_path = os.path.join(dir, file)
                test_file(full_path)
                                
def test_file(sfzfile: str):
    """
    Tests a SFZ file
    :param file: The SFZ file to test
    """
    # print(full_path)
    print("Testing", sfzfile)
    with open(sfzfile, 'r') as sfz_file:
        contents = sfz_file.read()
    pp = preprocessor.Preprocessor(contents, path=sfzfile)
    tokenized_buffer = []
    for frag in pp.retrieve():
        lex = lexer.Lexer(frag)
        tokenized_buffer += lex.tokenized_buffer
    parse = parser.Parser(tokenized_buffer)
    # Check that all include files can be accessed
    for item in parse.parsed_buf:
        if type(item) == sfztypes.Include:
            if not os.path.exists(item.full_path):
                raise FileNotFoundError(f"The SFZ include file \"{item.path}\" in file \"{sfzfile}\" cannot be found.")
            
    sample_groups = jsonifier.make_sample_dictionary(parse)
    # Check that all samples can be accessed
    for group in sample_groups:
        for sample_arr in group:
            for sample in sample_arr:
                if "sample" in sample:
                    if not os.path.exists(os.path.join(parse.source_file_path, sample["sample"])):
                        raise FileNotFoundError(f"The sample \"{sample['sample']}\" in file \"{sfzfile}\" cannot be found.")

if __name__ == "__main__":
    TEST_PATH = "D:\\Recording\\sfz"
    # test_dir_recursively(TEST_PATH)
    FILES = ["D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\01-full.sfz",]
            #  "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\02-basic.sfz",
            #  "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\03-kick.sfz",
            #  "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\04-snare.sfz",
            #  "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\05-toms.sfz",
            #  "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\06-hihat.sfz",
            #  "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\07-cymbals.sfz",
            #  "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\08-noises.sfz"]
    for file in FILES:
        test_file(file)
    print(GREEN + "All tests passed." + END_COLOR)
