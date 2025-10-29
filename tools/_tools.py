import time
import os
import sys
from exceptions import *
from collections import deque

def check_instance(variable: object, expected_type: type = None, length: int = None) -> None:
    if expected_type is not None:
        if not isinstance(variable, expected_type):
            raise WrongTypeError(f"Expected '{expected_type.__name__}', got '{type(variable).__name__}' instead")

    if length is not None:
        if isinstance(length, int) and length > 0:
            if not isinstance(variable, (str, list, tuple, dict, set, frozenset, bytes, bytearray, range)):
                raise WrongTypeError("length can only be checked on: (str, list, tuple, dict, set, frozenset, bytes, bytearray, range)")
            if len(variable) != length:
                raise WrongLengthError(f"Expected length '{length}', got '{len(variable)}' instead")
        else:
            raise ValueError(f"length must be provided as a positive integer")

def isdigit(string: str) -> bool:
    try:
        if not isinstance(string, str):
            raise WrongTypeError("called isdigit() on a non-string object")
        return all(c in "0123456789" for c in string)
    except KeyError as e:
        print(e)
        return False

class InstanceManager:
    instances = {}
    instances_memory_addresses = {}

    @classmethod
    def push(cls, instance: str, current_instances: int, max_instances: int, instances_addresses: deque[object]) -> None:
        cls.instances.update({
            instance: {"active instances": current_instances, "max_instances": max_instances}
        })
        cls.instances_memory_addresses.update({
            instance: ["0x" + hex(id(address))[2:].upper().rjust(16,"0") for address in instances_addresses]
        })

def Singleton(max_instances: int = 1) -> object:
    if max_instances < 1 or not isinstance(max_instances, int):
        raise WrongTypeError("max_instances must be a positive integer")

    class _SingletonBase:
        if _allowed_inf:
            instances: deque[object] = deque(maxlen=max_instances)

        def __new__(cls, *args: tuple, **kwargs: dict) -> object:
            _number_of_instances = len(cls.instances)

            if _number_of_instances >= max_instances and not _allowed_inf:
                raise InstanceOverflowError(f"Cannot create more instances of \"{cls.__name__}\" limit={max_instances}")

            instance = super().__new__(cls)
            cls.instances.append(instance)
            InstanceManager.push(cls.__name__, len(cls.instances), max_instances, cls.instances)
            return instance

        def __getattribute__(self, item):
            cls = super().__getattribute__("__class__")
            instances = super().__getattribute__('instances')
            if self not in instances:
                raise UnknownInstanceError(f"This instance is not registered for \"{cls.__name__}\"")

            return super().__getattribute__(item)

        def kill(self) -> None:
            cls = self.__class__

            if self in cls.instances:
                cls.instances.remove(self)

            InstanceManager.push(cls.__name__, len(cls.instances), max_instances, cls.instances)

    return _SingletonBase

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