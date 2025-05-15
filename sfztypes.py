"""
File: sfztypes.py

This file represents different operations in a SFZ file.
"""

from enum import Enum
import os

class OpCodeHeader(Enum):
    """
    Represents the different SFZ headers.
    """
    REGION = 1
    GROUP = 2
    CONTROL = 3
    GLOBAL = 4
    CURVE = 5
    EFFECT = 6
    MASTER = 7
    MIDI = 8
    SAMPLE = 9

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
