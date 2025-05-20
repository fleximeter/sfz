"""
File: unittests_lexer.py

Unit tests for the lexer
"""

import unittest
import lexer

class TestLineLexer(unittest.TestCase):
    def test_comment(self):
        path = "/home/test/file.sfz"
        contents = "// This is a comment"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 1)
        contents = "// This is a comment\ngarbage"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 1)

    def test_header(self):
        path = "/home/test/file.sfz"
        contents = "<region>"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 1)
        self.assertEquals(lex.tokenized_buffer[0].token_type, lexer.TokenType.HEADER)
        self.assertEquals(lex.tokenized_buffer[0].lexeme, "<region>")
    
    def test_key_value(self):
        path = "/home/test/file.sfz"
        
        contents = "mykey=myval"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 3)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.KEY)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "mykey")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.OPERATOR)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "=")
        self.assertEqual(lex.tokenized_buffer[2].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[2].lexeme, "myval")

        contents = "mykey = myval"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 3)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.KEY)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "mykey")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.OPERATOR)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "=")
        self.assertEqual(lex.tokenized_buffer[2].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[2].lexeme, "myval")
        
        contents = "mykey = myval mykey2 = myval2"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 6)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.KEY)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "mykey")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.OPERATOR)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "=")
        self.assertEqual(lex.tokenized_buffer[2].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[2].lexeme, "myval")
        self.assertEqual(lex.tokenized_buffer[3].token_type, lexer.TokenType.KEY)
        self.assertEqual(lex.tokenized_buffer[3].lexeme, "mykey2")
        self.assertEqual(lex.tokenized_buffer[4].token_type, lexer.TokenType.OPERATOR)
        self.assertEqual(lex.tokenized_buffer[4].lexeme, "=")
        self.assertEqual(lex.tokenized_buffer[5].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[5].lexeme, "myval2")
        
        contents = "mykey = myval // a comment here\n"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 4)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.KEY)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "mykey")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.OPERATOR)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "=")
        self.assertEqual(lex.tokenized_buffer[2].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[2].lexeme, "myval ")
        self.assertEqual(lex.tokenized_buffer[3].token_type, lexer.TokenType.COMMENT)
        self.assertEqual(lex.tokenized_buffer[3].lexeme, "// a comment here")
        
        contents = "mykey = myval mykey2 = myval2 // a comment here\n"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 7)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.KEY)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "mykey")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.OPERATOR)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "=")
        self.assertEqual(lex.tokenized_buffer[2].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[2].lexeme, "myval")
        self.assertEqual(lex.tokenized_buffer[3].token_type, lexer.TokenType.KEY)
        self.assertEqual(lex.tokenized_buffer[3].lexeme, "mykey2")
        self.assertEqual(lex.tokenized_buffer[4].token_type, lexer.TokenType.OPERATOR)
        self.assertEqual(lex.tokenized_buffer[4].lexeme, "=")
        self.assertEqual(lex.tokenized_buffer[5].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[5].lexeme, "myval2 ")
        self.assertEqual(lex.tokenized_buffer[6].token_type, lexer.TokenType.COMMENT)
        self.assertEqual(lex.tokenized_buffer[6].lexeme, "// a comment here")

    def test_include(self):
        path = "/home/test/file.sfz"
        
        contents = "#include \"myfile.sfz\""
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 2)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.INCLUDE)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "#include")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "myfile.sfz")

        contents = "#include  \t \"subdir/myfile.sfz\""
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 2)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.INCLUDE)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "#include")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "subdir/myfile.sfz")

    def test_define(self):
        path = "/home/test/file.sfz"
        contents = "#define $mydef myval"
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 3)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.DEFINE)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "#define")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "$mydef")
        self.assertEqual(lex.tokenized_buffer[2].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[2].lexeme, "myval")

        contents = "#define \t $a \t  2 \t "
        lex = lexer.LineLexer(contents, 5, path)
        self.assertTrue(len(lex.tokenized_buffer) == 3)
        self.assertEqual(lex.tokenized_buffer[0].token_type, lexer.TokenType.DEFINE)
        self.assertEqual(lex.tokenized_buffer[0].lexeme, "#define")
        self.assertEqual(lex.tokenized_buffer[1].token_type, lexer.TokenType.STRING_VALUE)
        self.assertEqual(lex.tokenized_buffer[1].lexeme, "$a")
        self.assertEqual(lex.tokenized_buffer[2].token_type, lexer.TokenType.INT_VALUE)
        self.assertEqual(lex.tokenized_buffer[2].lexeme, 2)

if __name__ == "__main__":
    unittest.main()