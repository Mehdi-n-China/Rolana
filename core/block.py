
import time
import hashlib

import CONSTANTS
from Mempool import Mempool
from core.transaction import TransactionContainer
from ._crypto import signMessage, makePair, format, validateSignature

class BlockContainer:
    def __init__(self, index: int, previousHash: str, txs: list[TransactionContainer], ) -> None:
        self.index = index
        self.timestamp = time.time()
        self.txs = Mempool.importSet(CONSTANTS.BLOCK.MAX_TXS)
        self.previousHash = previousHash
        self.signatures = []
        self.hash = None

    def __str__(self) -> str:
        return "\n".join(str(tx) for tx in self.txs)


    def seal(self) -> str | None:
        if len(self.signatures) < CONSTANTS.CONSENSUS.MIN_SIGNATURES:
            return None
        return hashlib.sha256(str(self.signatures).encode()).hexdigest()

    def importMempool(self, Mempool: object) -> None:
        """
        Imports transactions from Mempool.txs into the block, with optional priority logic.
        """
        pass



