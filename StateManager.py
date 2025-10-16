
from collections import OrderedDict
from dataclasses import dataclass

import random
import time

class BiggestBalances:
    def __init__(self):
        self.balances = []

    def add(self, key, balance):
        self.balances.append((balance, key))

    def fetch(self):
        return self.balances.sort(reverse=True)

start = time.time()
dictionary = OrderedDict()
biggestBalances = BiggestBalances()

for i in range(10_000_000):
    account = {10000000-i: random.randint(1, 1_000_000)}
    dictionary.update(account)
    if i % 10_000 == 0:
        print(i)
print(time.time()-start)

keys = list(dictionary.keys())
values = list(dictionary.values())

start = time.time()

print(random.choices(keys, values, k=69))

print(time.time()-start)

@dataclass
class AccountState:
    """Single account state in RAM."""
    balance: int = 0  # liquid balance
    locked_balance: int = 0  # staked / locked balance
    nonce: int = 0  # transaction counter
    is_validator: bool = False  # validator flag

    def __repr__(self):
        return (f"<AccountState bal={self.balance}, locked={self.locked_balance}, "
                f"nonce={self.nonce}, validator={self.is_validator}>")

class StateCache:
    """Main RAM state with OrderedDict for LRU eviction + dirty tracking."""

    def __init__(self):
        self.accounts: OrderedDict[str, AccountState] = OrderedDict()  # addr -> account
        self.dirty: set[str] = set()  # accounts modified since last flush

    def get_account(self, address: str) -> AccountState:
        if address not in self.accounts:
            self.accounts[address] = AccountState()
        return self.accounts[address]

    def update_balance(self, address: str, delta: int):
        acc = self.get_account(address)
        acc.balance += delta
        self.dirty.add(address)
        self.accounts.move_to_end(address)

    def update_locked(self, address: str, delta: int):
        acc = self.get_account(address)
        acc.locked_balance += delta
        self.dirty.add(address)
        self.accounts.move_to_end(address)

    def increment_nonce(self, address: str):
        acc = self.get_account(address)
        acc.nonce += 1
        self.dirty.add(address)
        self.accounts.move_to_end(address)

    def set_validator(self, address: str, flag: bool):
        acc = self.get_account(address)
        acc.is_validator = flag
        self.dirty.add(address)
        self.accounts.move_to_end(address)

    def mark_clean(self, address: str):
        self.dirty.discard(address)

    def pop_oldest(self):
        if not self.accounts:
            return None
        addr, acc = self.accounts.popitem(last=False)
        self.dirty.discard(addr)
        return addr, acc

    def __repr__(self):
        return f"<StateCache accounts={len(self.accounts)} dirty={len(self.dirty)}>"
