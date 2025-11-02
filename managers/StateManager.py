
from .BaseManager import BaseManager
import sqlite3

from collections import OrderedDict

class StateManager(BaseManager):
    def __init__(self, god_manager):
        super().__init__(god_manager)
        self._state = OrderedDict()
        self._dirty_users = set()

    def get(self, key):
        if key in self._cache:
            return self._cache[key]
        else:
            account = self.send_with_response()


    def set(self, key, value, mark_dirty=True):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            oldest, _ = self.cache.popitem(last=False)
            # optionally flush oldest to disk
        if mark_dirty:
            self.dirty.add(key)

    def flush(self, writer):
        for key in list(self.dirty):
            writer(key, self.cache[key])
            self.dirty.remove(key)

class _Accpunts:
    def __init__(self, pub_key):
        self.pub_key = pub_key
        self.balance = balance
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