import os

from _base import CryptoError

class InvalidKeyError(CryptoError):
    def __init__(self) -> None:
        pass

class KeyGenerationError(CryptoError):
    def __init__(self) -> None:
        pass

class KeySerializationError(CryptoError):
    def __init__(self) -> None:
        pass

class MissingKeyError(CryptoError):
    def __init__(self, key_type) -> None:
        super().__init__(f"No valid {key_type} was found")


raise MissingKeyError("PrivateKey")


