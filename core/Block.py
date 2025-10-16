
import time
import hashlib

import CONSTANTS
from Mempool import Mempool
from Transaction import TransactionContainer
from core.Keys import Keys

class BlockContainer:
    def __init__(self, index: int, previousHash: str) -> None:
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


sk, pk = Keys.makePair()
sig = Keys.signMessage(sk, Keys.format(pk, "bet", 1, to=sk, amount=100, fee=100, game="100",
                                       params=["arg", "arg", "arg"]))

start = time.time()
for i in range(10000):

    tx = TransactionContainer(pk, "bet", 1, sig, to=sk, amount=100, fee=100, game="100", params=["arg", "arg", "arg"])

    Keys.validateSignature(tx.identity, tx.sig, tx.hash)
end = time.time()
print("Verification time:", end - start, "seconds")
