import preprocessor
import lexer
import parser

if __name__ == "__main__":
    # FILE = "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\01-full.sfz"
    FILE = "sample_files/test.sfz"
    with open(FILE, 'r') as sfz_file:
        contents = sfz_file.read()
    pp = preprocessor.Preprocessor(contents, path=FILE)
    tokenized_buffer = []
    for frag in pp.retrieve():
        lex = lexer.Lexer(frag)
        tokenized_buffer += lex.tokenized_buffer
    parse = parser.Parser(tokenized_buffer)