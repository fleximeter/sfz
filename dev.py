import preprocessor

if __name__ == "__main__":
    FILE = "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\01-full.sfz"
    with open(FILE, 'r') as sfz_file:
        contents = sfz_file.read()
    pp = preprocessor.Preprocessor(contents, file=FILE)
    print(pp.preprocessed_contents)
    print(pp.bindings)
