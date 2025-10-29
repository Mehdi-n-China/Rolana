from ._base import NetworkError

class NoPeerProvidedError(NetworkError):
    def __init__(self):
        super().__init__(f"Non-valid peer was provided")
