
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
        if key_type in ("PrivateKey", "PublicKey"):
            f"The provided {key_type} could not be found."
        else:
            self.key_type = f"Bad Argument"

raise MissingKeyError("PrivateKey")