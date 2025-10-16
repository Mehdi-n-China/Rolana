from Tools import *

class MempoolContainer:
    def __init__(self) -> None:
        self.txs = []
        self.txSet = set()

    def __str__(self) -> str:
        return "\n".join(str(tx) for tx in self.txs)

    def pack(self) -> str:
        return str([tx.raw for tx in self.txs])

    def packraw(self) -> str:
        return ";".join(tx.raw for tx in self.txs)


    def add(self, tx: object) -> None:
        if tx.hash in self.txSet:
            raise ValueError("TX rejected: duplicate")
        self.txs.append(tx)
        self.txSet.add(tx.hash)


    def importSet(self, numberOfTxs: int) -> list:
        if numberOfTxs > len(self.txs):
            numberOfTxs = len(self.txs)

        subset = self.txs[:numberOfTxs]
        del self.txs[:numberOfTxs]
        return subset

    def remove(self, tx: object) -> None:
        self.txs.remove(tx)


Mempool = MempoolContainer()