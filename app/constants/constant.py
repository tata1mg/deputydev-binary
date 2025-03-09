from enum import Enum


class KeywordTypes(Enum):
    FUNCTION = "function"
    CLASS = "class"
    FILE = "file"


class PropertyTypes(Enum):
    FUNCTION = "functions"
    CLASS = "classes"
    FILE = "file_path"
