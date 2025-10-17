
from ._base import BuiltinError

class WrongTypeError(BuiltinError):
    def __init__(self, msg):
        super().__init__(msg)

class WrongLengthError(BuiltinError):
    def __init__(self, msg):
        super().__init__(msg)
