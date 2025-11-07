from typing import Any

from .BaseManager import BaseManager

from collections import OrderedDict
import CONSTANTS

class StateManager(BaseManager):
    def __init__(self, god_manager: object) -> None:
        super().__init__(god_manager)
        self._cache = OrderedDict()
        self._dirty_users = dict()

    def _get(self, key: str) -> object:
        if key in self._cache:
            return self._cache[key]
        else:
            account = self.send_with_response("StateDBManager", {"cmd": "get", "key": key})
            return account

    def _set(self, key, account) -> None:
        self._cache.update({key: account})
        self._dirty_users.update({key: account})
        if len(self._cache) > CONSTANTS.STATE.MAX_CACHE:
            self._dirty_users.update({key: account for key, account in self._cache.popitem(last=False)})


    def _flush(self):
        self.send("StateDBManager", {"cmd": "flush", "accounts": self._dirty_users})
        self._dirty_users.clear()

    def _main(self):
        while True:
            msgs = self.await_drain_inbox()
            for msg in msgs:
                handle_msg(msg)

    def handle_msg(self, msg):
        match msg.get("cmd"):
            case "get":
                self.reply(msg, self.get(msg.get("key")))

            case "set":
                msg

            case _:
                raise RuntimeError()


class _Accounts:
    def __init__(self, pub_key, balance, nonce):
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