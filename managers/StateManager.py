from typing import Any
from .BaseManager import BaseManager
from collections import OrderedDict
import CONSTANTS

class StateManager(BaseManager):
    def __init__(self, god_manager: object) -> None:
        super().__init__(god_manager)
        self._cache = OrderedDict()
        self._dirty_users = dict()
        self._dirty_globals = dict()

    def _get(self, key: str) -> object:
        if key in self._cache:
            return self._cache[key]
        else:
            account = self.send_with_response("StateDBManager", {"cmd": "get", "key": key})
            return account

    def _set(self, _type: str, key: str, data: dict[str, Any]) -> None:
        self._cache.update({key: data})
        if _type == "accounts":
            self._dirty_users.update({key: data})
            if len(self._cache) > CONSTANTS.STATE.MAX_CACHE:
                self._dirty_users.update({key: data for key, data in self._cache.popitem(last=False)})
                self._flush()

        elif _type == "globals":
            self._cache.update({key: data})
            self._dirty_globals.update({key: data})

        else:
            raise RuntimeError(f"Unknown type: {_type}")

    def _flush(self) -> None:
        self.send("StateDBManager", {"cmd": "set", "type": "accounts", "data": self._dirty_users})
        self._dirty_users.clear()

    def _main(self) -> None:
        while True:
            msgs = self.await_drain_inbox()
            for msg in msgs:
                self.handle_msg(msg)

    def handle_msg(self, msg: dict[str, Any]) -> None:
        match msg.get("cmd"):
            case "get":
                self.reply(msg, self._get(msg.get("key")))

            case "set":
                self._set(msg.get("type"), msg.get("key"), msg.get("data"))

            case _:
                raise RuntimeError(f"Unknown command: {msg.get('cmd')}")


class _Accounts:
    def __init__(self, pub_key, balance, nonce) -> None:
        self.pub_key = pub_key
        self.balance = balance
        self.locked_balance = locked_balance
        self.nonce = nonce
        self.

class _Chains:
    def __init__(self, pub_key):
        self.height = height
        self.previous_hash
        self.latest_timestamp
        self.total_txs
        self.total

class _Validators:
    def __init__(self, pub_key):
        self.pub_key = pub_key