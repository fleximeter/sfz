# sfz

This is a Python implementation for a SFZ sample file metadata parser. It is intended to port easily into other programming languages. The workflow for using this program goes like this:

```
FILE = "my file path"
with open(FILE, 'r') as sfz_file:
    contents = sfz_file.read()
lex = lexer.Lexer(contents)
parse = parser.Parser(lex, FILE)
```

The parsed contents will be located in `parse.parsed_buf`.

## Testing

To test this parser, run `tests.py` and set the `TEST_PATH` to the path of a directory containing SFZ files to test. The parser will parse the files and check the paths of all samples and include files.
