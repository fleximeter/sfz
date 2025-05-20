"""
File: unittests_preprocessor.py

Unit tests for the preprocessor
"""

import unittest
import preprocessor

class TestPreprocessor(unittest.TestCase):
    def test(self):
        # An empty preprocessor
        pp = preprocessor.Preprocessor(sfz_contents="", path="")

        sfz_contents = "<control>\n" \
            "default_path=test_code\n" \
            "#define $mykey what\n" \
            "#define $mykey2 5.0\n" \
            "#define $mykey3 2\n" \
            "\n" \
            "<group>\n" \
            "my$mykey = $mykey2\n" \
            "a$mykey= $mykey3\n" \
            "akey = aval akey2 = aval2\n" \
            "huh$mykey=$mykey3\n"
        
        sfz_out = "<control>\n" \
            "default_path=test_code\n" \
            "#define $mykey what\n" \
            "#define $mykey2 5.0\n" \
            "#define $mykey3 2\n" \
            "\n" \
            "<group>\n" \
            "mywhat = 5.0\n" \
            "awhat= 2\n" \
            "akey = aval akey2 = aval2\n" \
            "huhwhat=2\n"
        pp = preprocessor.Preprocessor(sfz_contents=sfz_contents, path="")
        self.assertEqual(pp.retrieve()[0].contents, sfz_out)

if __name__ == "__main__":
    unittest.main()
    