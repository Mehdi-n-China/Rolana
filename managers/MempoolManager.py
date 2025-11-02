
from .BaseManager import BaseManager
from core import TransactionContainer
from itertools import islice
import CONSTANTS
import time

class MempoolManager(BaseManager):
    def __init__(self, god_manager) -> None:
        super().__init__(god_manager)
        self.txs = set()
        self._import_requested = False
        self._last_block_timestamp = time.perf_counter()
        self._txs_requested = 0

    def __str__(self) -> str:
        return "\n".join(str(tx) for tx in self.txs)

    def add(self, txs: list[TransactionContainer]) -> None:
        self.txs.update(txs)

    def remove(self, txs: list[TransactionContainer]) -> None:
        self.txs.difference_update(txs)

    def import_set(self, number_of_txs: int) -> list:
        number_of_txs = min(number_of_txs, len(self.txs))
        subset = list(islice(self.txs, number_of_txs))
        self.txs.difference_update(subset)
        return subset

    def _main(self):
        while True:
            msgs = self.await_drain_inbox()
            for msg in msgs:
                self.handle_msg(msg)

    def handle_msg(self, msg) -> None:
        match msg.get("cmd", None):
            case "add":
                self.add(msg.get("txs", []))
                if self._import_requested:
                    if (time.perf_counter() - self._last_block_timestamp > CONSTANTS.BLOCK.MAX_FILL_TIME or
                        len(self.txs) >= self._txs_requested):
                        self.reply(msg, self.import_set(self._txs_requested))
                        self._last_block_timestamp = time.perf_counter()
                        self._import_requested = False

            case "remove":
                self.remove(msg.get("txs", []))
                if self._import_requested:
                    if (time.perf_counter() - self._last_block_timestamp > CONSTANTS.BLOCK.MAX_FILL_TIME or
                        len(self.txs) >= self._txs_requested):
                        self.reply(msg, self.import_set(self._txs_requested))
                        self._last_block_timestamp = time.perf_counter()
                        self._import_requested = False

            case "import":
                if (time.perf_counter() - self._last_block_timestamp > CONSTANTS.BLOCK.MAX_FILL_TIME or
                    len(self.txs) >= msg.get("number_of_txs", 0)):
                    self.reply(msg, self.import_set(msg.get("number_of_txs", 0)))
                    self._import_requested = False
                    self._last_block_timestamp = time.perf_counter()
                else:
                    self._txs_requested = msg.get("number_of_txs", 0)
                    self._import_requested = True


