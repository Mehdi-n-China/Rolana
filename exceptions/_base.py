
import time
import os
import traceback

class Logger:
    COLORS = {
        "tx": "\033[92m",       # green
        "block": "\033[94m",    # blue
        "network": "\033[93m",  # yellow
        "general": "\033[0m",   # reset/white
        "error": "\033[91m",    # red
    }
    RESET = "\033[0m"

    def __init__(self, base_dir="logs"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

        self.channels = {}

    def _write(self, channel, msg):
        # initialize log files
        for path in self.channels.values():
            if not os.path.exists(path):
                with open(path, "w") as f:
                    f.write("=== LOG START ===\n")

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{channel.upper()}] {timestamp} - {msg}"

        # console with color
        color = self.COLORS.get(channel, self.RESET)
        print(color + formatted + self.RESET)

        # append to file
        with open(self.channels[channel], "a", encoding="utf-8") as f:
            f.write(formatted + "\n")

    # convenience
    def tx(self, msg): self._write("tx", msg)
    def block(self, msg): self._write("block", msg)
    def network(self, msg): self._write("network", msg)
    def general(self, msg): self._write("general", msg)

    # special error logger with traceback capture
    def error(self, msg, exc=None):
        if exc:
            tb = traceback.format_exc()
            msg = f"{msg}\n{tb}"
        self._write("error", msg)


class CryptoError(Exception):
    def __init__(self) -> None:
        pass

    def _throw(self):
        pass