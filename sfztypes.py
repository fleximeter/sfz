"""
File: sfztypes.py

This file represents different operations in a SFZ file.
"""

from enum import Enum
import os

class OpCodeHeader(Enum):
    """
    Represents the different SFZ headers.
    In some cases, there is no header, so the NO_HEADER opcode is provided for this.
    """
    NO_HEADER = 1
    REGION = 2
    GROUP = 3
    CONTROL = 4
    GLOBAL = 5
    CURVE = 6
    EFFECT = 7
    MASTER = 8
    MIDI = 9
    SAMPLE = 10

class SfzToken:
    def __init__(self):
        pass

class Include(SfzToken):
    """
    Represents a SFZ include path
    """
    def __init__(self, path: str, context_path: str):
        """
        Creates a new `Include`
        :param path: The path to include
        :param context_path: The context path for inclusion
        """
        super(SfzToken, self).__init__()
        self.path = path
        self.context_path = context_path
        self.full_path = os.path.join(context_path, path)

class Define(SfzToken):
    """
    Represents a SFZ define macro
    """
    def __init__(self, name: str, value):
        """
        Creates a new `Define` macro binding
        :param name: The name of the definition
        :param value: The associated value
        """
        super(SfzToken, self).__init__()
        self.name = name
        self.value = value

class Header(SfzToken):
    """
    Represents a SFZ header and its associated data
    """
    def __init__(self, header: OpCodeHeader):
        """
        Creates a new `Header`
        :param header: The header type
        """
        super(SfzToken, self).__init__()
        self.header = header
        self.attributes = {}
    
    def add_attribute(self, key, val):
        """
        Adds a key/value pair to the attributes dictionary
        :param key: The key
        :param val: The value
        """
        self.attributes[key] = val
