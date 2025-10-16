import time
import os


def checkInstance(variable: object, expectedType: type = None, length: int = None) -> None:
    if expectedType is not None:
        if not isinstance(variable, expectedType):
            raise TypeError(f"Expected '{expectedType.__name__}', got '{type(variable).__name__}' instead")

    if length is not None:
        if isinstance(length, int) and length > 0:
            if not isinstance(variable, (str, list, tuple, dict, set, frozenset, bytes, bytearray, range)):
                raise TypeError("length can only be checked on: (str, list, tuple, dict, set, frozenset, bytes, bytearray, range)")
            if len(variable) != length:
                raise OverflowError(f"Expected length '{length}', got '{len(variable)}' instead")
        else:
            raise ValueError(f"length must be provided as a positive integer")

def isdigit(string: str) -> bool:
    try:
        if not isinstance(string, str):
            raise TypeError("called isdigit() on a non-string object")
        return all(c in "0123456789" for c in string)
    except Exception as e:
        raiseError(e)

class Logger:
    def __init__(self, base_dir="logs"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        # hardcoded channels
        self.channels = {
            "tx": os.path.join(self.base_dir, "tx.log"),
            "block": os.path.join(self.base_dir, "block.log"),
            "network": os.path.join(self.base_dir, "network.log"),
            "general": os.path.join(self.base_dir, "general.log"),
        }

        for path in self.channels.values():
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write("=== LOG START ===\n")

    def _write(self, channel, msg):
        if channel not in self.channels:
            channel = "general"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{channel.upper()}] {timestamp} - {msg}"
        print(formatted)
        with open(self.channels[channel], "a") as f:
            f.write(formatted + "\n")

    def tx(self, msg): self._write("tx", msg)
    def block(self, msg): self._write("block", msg)
    def network(self, msg): self._write("network", msg)
    def general(self, msg): self._write("general", msg)