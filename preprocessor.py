"""
File: preprocessor.py

This is a preprocessor that handles macros like #include and #define.
"""

from io import StringIO
import os
import pathlib

class SfzPreprocessorError(SyntaxError):
    """
    Represents a preprocessor error in a SFZ file
    """
    def __init__(self, msg):
        super(SfzPreprocessorError, self).__init__()
        self.msg = msg

class Preprocessor:
    """
    Manages the preprocessing step for a SFZ file, before the lexing step.
    """
    def __init__(self, sfz_contents, **kwargs):
        """
        Creates a new Preprocessor for a SFZ file.
        :param sfz_contents: The contents of the SFZ file
        Additional parameters for `kwargs`:
        `path`: The SFZ file path
        `bindings`: Key/value bindings to pass down from the parent
        """
        self.sfz_contents = sfz_contents
        self.i = 0
        if "path" in kwargs:
            self.path = kwargs["path"]
        else:
            self.path = ""
        if "bindings" in kwargs:
            self.bindings = kwargs["bindings"].copy()
        else:
            self.bindings = {}
        self.preprocessed_contents = StringIO()
        self.process()
        self.preprocessed_contents.seek(0)
        self.preprocessed_contents = self.preprocessed_contents.read()

    def process(self):
        """
        Manages the preprocessing.
        """
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == '#':
                self.macrodef()
            elif self.sfz_contents[self.i] == '$':
                self.substitute()
            else:
                self.preprocessed_contents.write(self.sfz_contents[self.i])
                self.i += 1

    def macrodef(self):
        """
        Handles macro definitions.
        """
        LIMIT = 20
        idx = self.i + 1
        while idx < len(self.sfz_contents) and idx - self.i < LIMIT:
            if self.sfz_contents[idx] == ' ' or self.sfz_contents[idx] == '\t':
                break
            idx += 1
        substr = self.sfz_contents[self.i:idx]
        if substr == "#include":
            self.preprocessed_contents.write(substr)
            self.i = idx
            self.include()
        elif substr == "#define":
            self.preprocessed_contents.write(substr)
            self.i = idx
            self.define()
        else:
            raise SfzPreprocessorError(f"Unknown macro \"{substr}\" in file {self.path} at index {self.i}.")

    def include(self):
        """
        Manages include macros
        """
        # this code just identifies the include path for now, doesn't load the file
        start_macro_idx = self.i
        start_idx = -1
        end_idx = -1
        include_path = ""

        # get the start index of the include path
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == '\"' or self.sfz_contents[self.i] == '\'':
                start_idx = self.i + 1
                self.i += 1
                break
            elif self.sfz_contents[self.i] != ' ' and self.sfz_contents[self.i] != '\t':
                raise SfzPreprocessorError(f"Unexpected character \'{self.sfz_contents[self.i]}\' in file {self.path} at index {self.i} after #include macro definition.")
            else:
                self.i += 1

        # get the end index of the include path
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == '\"' or self.sfz_contents[self.i] == '\'':
                end_idx = self.i
                self.i += 1
                break
            else:
                self.i += 1

        if start_idx >= end_idx:
            raise SfzPreprocessorError(f"Improperly formatted include path in file {self.path} at index {self.i} after #include macro definition.")

        else:
            include_path = self.sfz_contents[start_idx:end_idx]
            # add the text of the macro include definition to the output buffer
            self.preprocessed_contents.write(self.sfz_contents[start_macro_idx:self.i])

    def define(self):
        """
        Manages define macros
        """
        start_macro_idx = self.i
        name_start_idx = -1
        name_end_idx = -1
        value_start_idx = -1
        value_end_idx = -1
        name = ""
        value = ""

        # get the start index of the name
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == '$':
                name_start_idx = self.i
                self.i += 1
                break
            elif self.sfz_contents[self.i] != ' ' and self.sfz_contents[self.i] != '\t':
                raise SfzPreprocessorError(f"Unexpected character \'{self.sfz_contents[self.i]}\' in file {self.path} at index {self.i} after #define macro definition.")
            else:
                self.i += 1

        # get the end index of the name
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == ' ' or self.sfz_contents[self.i] == '\t':
                name_end_idx = self.i
                self.i += 1
                break
            else:
                self.i += 1

        if name_start_idx >= name_end_idx:
            raise SfzPreprocessorError(f"Improperly formatted name in file {self.path} at index {self.i} after #define macro definition.")

        # get the start index of the value
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] != ' ' and self.sfz_contents[self.i] != '\t':
                value_start_idx = self.i
                self.i += 1
                break
            else:
                self.i += 1

        # get the end index of the value
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i].isspace():
                value_end_idx = self.i
                self.i += 1
                break
            else:
                self.i += 1

        if value_start_idx >= value_end_idx:
            raise SfzPreprocessorError(f"Improperly formatted value in file {self.path} at index {self.i} after #define macro definition.")

        name = self.sfz_contents[name_start_idx:name_end_idx]
        value = self.sfz_contents[value_start_idx:value_end_idx]
        self.bindings[name] = value

        # add the text of the macro define definition to the output buffer
        self.preprocessed_contents.write(self.sfz_contents[start_macro_idx:self.i])

    def substitute(self):
        """
        Manages #define substitutions
        """
        # why would anyone want a define name longer than 50 characters?
        LENGTH=50
        idx = self.i
        while idx < len(self.sfz_contents) and idx - self.i < LENGTH:
            candidate_key = self.sfz_contents[self.i:idx]
            if candidate_key in self.bindings:
                self.preprocessed_contents.write(self.bindings[candidate_key])
                self.i = idx
                return
            idx += 1
        raise SfzPreprocessorError(f"Could not find reference \"{self.sfz_contents[self.i:idx]}\" in the macro definition list in file {self.path} at index {self.i}.")
        


#                     absolute_include_path = os.path.join(str(pathlib.Path(self.path).parent), include_path)

# # If we are recursively evaluating included files, go ahead and lex them into the buffer
#                     if self.recursive:
#                         if os.path.exists(absolute_include_path):
#                             with open(absolute_include_path, 'r') as subsfz:
#                                 contents = subsfz.read()
#                                 sublex = Lexer(contents, self.recursive, absolute_include_path)
#                                 self.tokenized_buffer += sublex.tokenized_buffer
#                         else:
#                             raise SfzSyntaxError(f"Cannot find the path for the include file \"{include_path}\" at line {self.line_no + 1}, file \"{self.path}\"")
                    