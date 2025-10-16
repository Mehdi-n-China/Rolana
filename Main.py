import hashlib
import random
import time


class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def to_dict(self):
        return {"sender": self.sender, "receiver": self.receiver, "amount": self.amount}

class Block:
    def __init__(self, index, transactions, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()

    def compute_hash(self):

        tx_data = "".join([str(tx.__str__()) for tx in self.transactions])
        block_string = f"{self.index}{tx_data}{self.prev_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.mempool = []

    def create_genesis_block(self):
        return Block(0, [], "0"*64)

    def add_transaction(self, sender, receiver, amount):
        tx = Transaction(sender, receiver, amount)
        self.mempool.append(tx)

    def add_block(self):
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), self.mempool, prev_block.hash)
        self.chain.append(new_block)
        self.mempool = []
        return new_block

    def calculate_balances(self):
        balances = {}
        for block in self.chain:
            for tx in block.transactions:
                balances[tx.sender] = balances.get(tx.sender, 1000) - tx.amount
                balances[tx.receiver] = balances.get(tx.receiver, 1000) + tx.amount
        return balances

    def copy(self):
        new_chain = Blockchain()
        new_chain.chain = list(self.chain)
        return new_chain

# Simulate multiple nodes
NUM_NODES = 100
nodes = [Blockchain() for _ in range(NUM_NODES)]

# Generate random transactions
wallets = [f"0x{hashlib.sha1(str(i).encode()).hexdigest()[:40]}" for i in range(100)]

for _ in range(10):  # 10 blocks
    for node in nodes:
        for _ in range(1000):  # 10 TXs per block
            s, r = random.sample(wallets, 2)
            amt = random.randint(1, 10)
            node.add_transaction(s, r, amt)
        new_block = node.add_block()
        # Broadcast to other nodes
        for other in nodes:
            if other is not node:
                # simple longest chain adoption
                if len(node.chain) > len(other.chain):
                    other.chain = list(node.chain)
