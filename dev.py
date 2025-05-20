import preprocessor

if __name__ == "__main__":
    FILE = "D:\\Recording\\sfz\\Big_Rusty_Drums_1100\\Programs\\01-full.sfz"
    FILE = "sample_files/test.sfz"
    with open(FILE, 'r') as sfz_file:
        contents = sfz_file.read()
    pp = preprocessor.Preprocessor(contents, path=FILE)
    print(len(pp.retrieve()))
    for i in range(len(pp.retrieve())):
        print(pp.retrieve()[i].starting_line_number)
        print(pp.retrieve()[i].contents)
    # print(pp.preprocessed_contents)
    # print(pp.bindings)
