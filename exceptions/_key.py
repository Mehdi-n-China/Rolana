
from ._base import KeyError

class InvalidKeyError(KeyError):
    """Meant to be raised when an invalid key is encountered"""
    def __init__(self) -> None:
        pass

class KeyGenerationError(KeyError):
    """Meant to be raised when the process fails to create a key"""
    def __init__(self) -> None:
        pass

class KeySerializationError(KeyError):
    """Meant to be raised when a key serialization fails"""
    def __init__(self) -> None:
        pass

class MissingKeyError(KeyError):
    """Meant to be raised when a key is missing"""
    def __init__(self, key_type) -> None:
        super().__init__(f"No valid {key_type} was found")

class KeyMismatchError(KeyError):
    """Meant to be raised when a key pair is mismatched"""
    def __init__(self) -> None:
        super().__init__(f"The key pair is invalid")
