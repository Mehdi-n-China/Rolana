
from .BaseManager import BaseManager
from core import BlockContainer

class BlockManager(BaseManager):
    def __init__(self, god_manager):
        super().__init__(god_manager)
        self._block: BlockContainer | None = None
        self._index, self._last_hash =

    def _load_from_state(self):

    def _main(self) -> None:
        while True:
            txs = self.send_with_response("MempoolManager", {"cmd": "import"})
            self.send("NetworkManager", {"cmd": "gossip_block", "block": BlockContainer(txs)})
