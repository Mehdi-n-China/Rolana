import hashlib, timeit, random

# --- Mock CONSTANTS for test ---
class CONSTANTS:
    class TX:
        TYPES = ["transfer"]
        TRANSFER_REQUIREMENTS = ["to", "amount", "fee", "game", "params"]


# --- Helper for validation (mock version) ---
def checkInstance(value, _type, length=None):
    if not isinstance(value, _type):
        raise TypeError(f"Expected {_type}, got {type(value)}")
    if length and len(value) != length:
        raise ValueError(f"Invalid length for {value}")


# --- Class version ---
class TransactionContainer:
    def __init__(self, identity: bytes, type: str, nonce: int, sig: bytes, **kwargs) -> None:
        self.isValid = False

        checkInstance(identity, bytes, 32)
        self.identity = identity

        checkInstance(type, str)
        if type not in CONSTANTS.TX.TYPES:
            raise TypeError(f"'{type}' is not a valid transaction type! -> Valid types: {CONSTANTS.TX.TYPES}")
        self.type = type

        checkInstance(nonce, int)
        self.nonce = nonce

        self.to = to = kwargs.get("to")
        checkInstance(to, bytes)

        self.amount = amount = kwargs.get("amount")
        checkInstance(amount, int)

        self.fee = fee = kwargs.get("fee")
        checkInstance(fee, int)
        if self.fee < 0:
            raise ValueError(f"Invalid fee value: {fee}")

        self.game = game = kwargs.get("game")
        checkInstance(game, str)

        self.params = params = kwargs.get("params")
        checkInstance(params, list)

        requiredFields = getattr(CONSTANTS.TX, f"{type.upper()}_REQUIREMENTS")
        missing = [field for field in requiredFields if getattr(self, field) is None]
        if missing:
            raise ValueError(f"Missing fields: {missing}")

        checkInstance(sig, bytes, 64)
        self.sig = sig

        self.hash = hashlib.sha256(
            str(
                self.identity.hex()
                + self.type
                + str(self.nonce)
                + self.to.hex()
                + str(self.amount)
                + str(self.fee)
                + self.game
                + str(self.params)
            ).encode()
        ).hexdigest()

        self.isValid = True


# --- Dict version ---
def make_transaction(identity: bytes, type_: str, nonce: int, sig: bytes, to: bytes, amount: int, fee: int, game: str, params: list) -> dict:
    if type_ not in CONSTANTS.TX.TYPES:
        raise ValueError(f"Invalid tx type: {type_}")

    tx_hash = hashlib.sha256(
        str(
            identity.hex()
            + type_
            + str(nonce)
            + to.hex()
            + str(amount)
            + str(fee)
            + game
            + str(params)
        ).encode()
    ).hexdigest()

    return {
        "isValid": True,
        "identity": identity,
        "type": type_,
        "nonce": nonce,
        "to": to,
        "amount": amount,
        "fee": fee,
        "game": game,
        "params": params,
        "sig": sig,
        "hash": tx_hash,
    }


# --- Random tx generator ---
def random_tx():
    return {
        "identity": random.randbytes(32),
        "type": "transfer",
        "nonce": random.randint(0, 1_000_000),
        "sig": random.randbytes(64),
        "to": random.randbytes(32),
        "amount": random.randint(1, 1_000_000),
        "fee": random.randint(1, 100),
        "game": "test_game",
        "params": ["param1", "param2"],
    }


# --- Benchmarks ---
def bench_class():
    for _ in range(10_000):
        tx = random_tx()
        TransactionContainer(**tx)


def bench_dict():
    for _ in range(10_000):
        tx = random_tx()
        make_transaction(
            tx["identity"],
            tx["type"],
            tx["nonce"],
            tx["sig"],
            tx["to"],
            tx["amount"],
            tx["fee"],
            tx["game"],
            tx["params"],
        )


if __name__ == "__main__":
    print("Benchmarking 10,000 tx creations...\n")

    class_time = timeit.timeit(bench_class, number=1)
    dict_time = timeit.timeit(bench_dict, number=1)

    print(f"Class: {class_time:.4f}s  ({10000/class_time:.1f} tx/sec)")
    print(f"Dict:  {dict_time:.4f}s  ({10000/dict_time:.1f} tx/sec)")
    print(f"Speedup: {class_time/dict_time:.2f}x faster\n")
