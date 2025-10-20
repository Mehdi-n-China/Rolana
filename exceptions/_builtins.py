
from ._base import BuiltinError

class WrongTypeError(BuiltinError):
    def __init__(self, msg: str):
        super().__init__(msg)

class WrongLengthError(BuiltinError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
