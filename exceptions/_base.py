
class _CryptoError(Exception):
    """This is the master class for the project related errors
    This should be the only type caught by try catch
    This should never be caught directly, it is only meant for structure and should never be caught."""
    def __init__(self, msg) -> None:
        super().__init__(msg)

class BuiltinError(_CryptoError):
    """Master exception for builtin related errors
    This is what should be used for catching"""
    def __init__(self, msg):
        super().__init__(msg)

class KeyError(_CryptoError):
    """Master exception for key related errors
    This is what should be used for catching"""
    def __init__(self, msg):
        super().__init__(msg)

class RequirementError(_CryptoError):
    """Master exception for requirements related errors
    This is what should be used for catching"""
    def __init__(self, msg):
        super().__init__(msg)