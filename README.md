# sfz

This is a Python implementation for a SFZ sample file metadata parser. Use cases include situations
where you need to read a SFZ file in Python for some reason. More specifically, this package
is intended to facilitate extracting SFZ data and converting it to JSON format for easier use
in SuperCollider and other audio synthesis platforms that can read JSON files.

The workflow for using this program goes like this:

```
import jsonifier
import lexer
import parser

FILE = "my file path"
with open(full_path, 'r') as sfz_file:
    contents = sfz_file.read()
pp = preprocessor.Preprocessor(contents, path=full_path)
tokenized_buffer = []
for frag in pp.retrieve():
    lex = lexer.Lexer(frag)
    tokenized_buffer += lex.tokenized_buffer
parse = parser.Parser(tokenized_buffer)
sample_dict = jsonifier.make_sample_dictionary(parse)
```

The parsed contents will be located in `parse.parsed_buf`, and a JSON-friendly version will be in `sample_dict`.

If you want to make a JSON file, you can run `converter.py` and pass a SFZ file as an argument. It will convert it
to a JSON file. For the sample paths to work correctly in the JSON file, note that you will need to keep the
JSON file in the same directory as the SFZ file.

## Testing

To test this parser, run `tests.py` and set the `TEST_PATH` to the path of a directory containing SFZ files to test. The parser will parse the files and check the paths of all samples and include files.
