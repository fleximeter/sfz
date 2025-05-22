"""
File: preprocessor.py

This is a preprocessor that handles macros like #include and #define.
"""

from io import StringIO
import os
import pathlib

class SourceFileFragment:
    """
    Represents a fragment of a source code file. This is used to avoid line number discrepancies at #include tokens.
    """
    def __init__(self, contents: str, path: str, starting_line_number: int):
        """
        Creates a SourceFileFragment
        :param contents: The contents of the source code file portion
        :param path: The path to the source code file
        :param starting_line_number: The starting line number of the fragment
        """
        self.contents = contents
        self.path = path
        self.starting_line_number = starting_line_number

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
    The preprocessor generates a list of SourceFileFragments. Each SourceFileFragment
    tells you which file it came from and what the starting line number is.
    This is done so that we can include #include files and still report syntax
    errors with line numbers and file locations effectively.
    The workflow for parsing a SFZ file is to first run the preprocessor, then
    dump the source file fragments through the lexer, then run the parser.
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
        self.line = 0
        self.starting_line = 0
        self.last_newline = -1  # tracks the index of the last newline
        if "path" in kwargs:
            self.path = kwargs["path"]
        else:
            self.path = ""
        if "bindings" in kwargs:
            self.bindings = kwargs["bindings"].copy()
        else:
            self.bindings = {}
        if "root_dir" in kwargs:
            self.root_dir = kwargs["root_dir"]
        elif "path" in kwargs:
            self.root_dir = pathlib.Path(kwargs["path"]).parent
        else:
            self.root_dir = ""
        self.source_file_fragments = []
        self.preprocessed_contents = StringIO()
        self.process()
        self.preprocessed_contents.seek(0)
        self.preprocessed_contents = self.preprocessed_contents.read()

    def retrieve(self):
        """
        Retrieves the preprocessed SFZ code
        :return: A list of SourceFileFragments
        """
        return self.source_file_fragments

    def process(self):
        """
        Manages the preprocessing.
        """
        while self.i < len(self.sfz_contents):
            # we can only have a macro definition if the # occurs as the first character
            # in the line or right after whitespace at the start of the line
            if self.sfz_contents[self.i] == '#' and \
                (self.sfz_contents[self.last_newline+1:self.i-1].isspace() or self.i - self.last_newline == 1 or self.i == 0):
                self.macrodef()
            elif self.sfz_contents[self.i] == '$':
                self.substitute()
            else:
                self.preprocessed_contents.write(self.sfz_contents[self.i])
                if self.sfz_contents[self.i] == '\n':
                    self.line += 1
                    self.last_newline = self.i
                self.i += 1

        # When the file is completely processed, check to see if there is any processed source code to
        # add to the list of SourceFileFragments. If so, add the last fragment.
        self.preprocessed_contents.seek(0)
        processed_contents = self.preprocessed_contents.read()
        if len(processed_contents) > 0:
            self.source_file_fragments.append(SourceFileFragment(processed_contents, self.path, self.starting_line))

    def macrodef(self):
        """
        Handles macro definitions.
        """
        LIMIT = 20
        idx = self.i + 1
        while idx < len(self.sfz_contents) and idx - self.i < LIMIT:
            if self.sfz_contents[idx].isspace():
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
            raise SfzPreprocessorError(f"Unknown macro \"{substr}\" in file \"{self.path}\" at line {self.line+1}.")

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
                raise SfzPreprocessorError(f"Unexpected character \'{self.sfz_contents[self.i]}\' in file \"{self.path}\" at line {self.line+1} after #include macro definition.")
            else:
                self.i += 1

        # get the end index of the include path
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == '\"' or self.sfz_contents[self.i] == '\'':
                end_idx = self.i
                self.i += 1
                break
            elif self.sfz_contents[self.i] == '\t':
                raise SfzPreprocessorError(f"Unexpected tab in file \"{self.path}\" at line {self.line+1} after #include macro definition.")
            elif self.sfz_contents[self.i] == '\n':
                raise SfzPreprocessorError(f"Unexpected newline in file \"{self.path}\" at line {self.line+1} after #include macro definition.")
            else:
                self.i += 1

        # read the rest of the line
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == '\n':
                self.last_newline = self.i
                self.i += 1
                break
            elif not self.sfz_contents[self.i].isspace():
                raise SfzPreprocessorError(f"Unexpected character \'{self.sfz_contents[self.i]}\' after include path in file \"{self.path}\" at line {self.line+1} after #include macro definition.")
            self.i += 1

        if start_idx >= end_idx:
            raise SfzPreprocessorError(f"Improperly formatted include path in file \"{self.path}\" at line {self.line+1} after #include macro definition.")

        else:
            # add the text of the macro include definition to the output buffer
            if self.sfz_contents[self.i-1] == '\n':
                self.preprocessed_contents.write(self.sfz_contents[start_macro_idx:self.i-1])
            else:
                self.preprocessed_contents.write(self.sfz_contents[start_macro_idx:self.i])

            include_str = self.sfz_contents[start_idx:end_idx]

            # The include path can either be relative to the include file, or relative to the original parent file.
            include_path = os.path.join(pathlib.Path(self.path).parent, include_str)
            global_include_path = os.path.join(self.root_dir, include_str)
            if os.path.exists(global_include_path) and not os.path.exists(include_path):
                include_path = global_include_path
            if os.path.exists(include_path):
                # we need to recursively preprocess the included code
                with open(include_path, 'r') as subfile:
                    subcontents = subfile.read()
                    subpreproc = Preprocessor(subcontents, path=include_path, root_dir=self.root_dir, bindings=self.bindings)
                    self.preprocessed_contents.seek(0)
                    processed_contents = self.preprocessed_contents.read()
                    if len(processed_contents) > 0:
                        self.source_file_fragments.append(SourceFileFragment(processed_contents, self.path, self.starting_line))
                        self.starting_line = self.line + 1
                        self.preprocessed_contents = StringIO()
                    for key, val in subpreproc.bindings.items():
                        self.bindings[key] = val
                    self.source_file_fragments += subpreproc.source_file_fragments
            else:
                raise SfzPreprocessorError(f"Could not locate the file \"{include_str}\" at line {self.line+1} after #include macro definition.")

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
                raise SfzPreprocessorError(f"Unexpected character \'{self.sfz_contents[self.i]}\' in file \"{self.path}\" at line {self.line+1} after #define macro definition.")
            elif self.sfz_contents[self.i] == '\n':
                raise SfzPreprocessorError(f"Unexpected newline in file \"{self.path}\" at line {self.line+1} after #define macro definition.")
            else:
                self.i += 1

        # get the end index of the name
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == ' ' or self.sfz_contents[self.i] == '\t':
                name_end_idx = self.i
                self.i += 1
                break
            elif self.sfz_contents[self.i] == '\n':
                raise SfzPreprocessorError(f"Unexpected newline in file \"{self.path}\" at line {self.line+1} after #define macro definition.")
            else:
                self.i += 1

        if name_start_idx >= name_end_idx:
            raise SfzPreprocessorError(f"Improperly formatted name in file \"{self.path}\" at line {self.line+1} after #define macro definition.")

        # get the start index of the value
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i] == '\n':
                raise SfzPreprocessorError(f"Unexpected newline in file \"{self.path}\" at line {self.line+1} after #define macro definition.")
            elif self.sfz_contents[self.i] != ' ' and self.sfz_contents[self.i] != '\t':
                value_start_idx = self.i
                self.i += 1
                break
            else:
                self.i += 1

        # get the end index of the value
        while self.i < len(self.sfz_contents):
            if self.sfz_contents[self.i].isspace():
                value_end_idx = self.i
                if self.sfz_contents[self.i] != '\n':
                    self.i += 1
                break
            else:
                self.i += 1
                value_end_idx = self.i
                
        if value_start_idx >= value_end_idx:
            raise SfzPreprocessorError(f"Improperly formatted value in file \"{self.path}\" at line {self.line+1} after #define macro definition.")

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
        idx = self.i + 1
        found_key = ""
        found_end_idx = -1
        while idx < len(self.sfz_contents) and idx - self.i < LENGTH and not self.sfz_contents[idx].isspace():
            if self.sfz_contents[self.i:idx] in self.bindings:
                found_key = self.sfz_contents[self.i:idx]
                found_end_idx = idx
            idx += 1
        if self.sfz_contents[self.i:idx] in self.bindings:
            found_key = self.sfz_contents[self.i:idx]
            found_end_idx = idx
        if found_key != "":
            self.preprocessed_contents.write(self.bindings[found_key])
            self.i = found_end_idx
        else:
            raise SfzPreprocessorError(f"Could not find reference \"{self.sfz_contents[self.i:idx]}\" in the macro definition list in file \"{self.path}\" at line {self.line+1}.")
        