from ._base import NetworkError

class NoPeerProvidedError(NetworkError):
    def __init__(self, function_name):
        super().__init__(f"No Valid Peer was provided to: {function_name}")