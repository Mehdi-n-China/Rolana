import time, hashlib, random
from typing import Any


def hash_to_roll(block_hash):
    # Convert hash to integer
    hash_int = int(block_hash, 16)

    # Normalize to 0-100
    roll = (hash_int % 1000000000000) / 10000000000  # 0.0000 - 100.0000

    return round(roll, 10)

def Dice(block_hash, side, target, amount):
    outcome = hash_to_roll(block_hash)
    if side == "under":
        if target < 1 or target > 99.9:
            return 0
        if outcome < target:
            multi = 99.9/target - 1
            payout = multi*amount
        else:
            payout = -amount
    elif side == "over":
        if target < 0.1 or target > 99:
            return 0
        if outcome > target:
            multi = 99.9/(100-target) - 1
            payout = multi*amount
        else:
            payout = -amount
    else:
        payout = 0

    return payout

class GameTools:
    class BasicFuncs:
        def __init__(self, block_hash: str) -> None:
            self.block_hash = block_hash

        def get_int(self, min: int = 1, max: int = 100) -> int:
            if any(isinstance(var, float) for var in (min, max)):
                raise TypeError("try get_float")
            if not all(isinstance(var, int) for var in (min, max)):
                raise TypeError("Variables must be integers")
            if max < min:
                raise ValueError("min must be smaller than max")
            random.seed(self.block_hash)
            return random.randint(min, max)

        def get_float(self, min: float | int = 0, max: (float, int) = 1) -> float:
            if not all(isinstance(var, (int, float)) for var in (min, max)):
                raise TypeError("Variables must be floats")
            if max < min:
                raise ValueError("min must be smaller than max")
            random.seed(self.block_hash)
            return random.uniform(min, max)

        def get_bool(self) -> bool:
            random.seed(self.block_hash)
            return random.choice([True, False])

        def get_number(self, min: int = 1, max: int = 100, step: int = 1) -> int:
            if not all(isinstance(var, int) for var in (min, max, step)):
                raise TypeError("Variables must be integers")
            if max < min:
                raise ValueError("min must be smaller than max")
            random.seed(self.block_hash)
            return random.randrange(min, max, step)

        def get_choice(self, array: list = None) -> str:
            if not array:
                array = [None]
            if not isinstance(array, list):
                raise TypeError("Array must be of type list")
            random.seed(self.block_hash)
            return random.choice(array)

        def get_choices(self, array: list = None, weights: list = None, k: int = 1) -> list:
            if not array:
                array = [None]
            if not isinstance(array, list):
                raise TypeError("Array must be of type list")
            if not isinstance(k, int):
                raise TypeError("K must be of type int")
            if k <= 0:
                raise ValueError("K must be at least 1")
            if weights:
                if not isinstance(weights, list):
                    raise TypeError("Weights must be of type list")
                if len(weights) != len(array):
                    print(len(weights), len(array))
                    raise TypeError("weights must have the same length as array")
                if not all(isinstance(weight, (int, float)) for weight in weights):
                    raise ValueError("All weights must be numbers")
                if any(weight <= 0 for weight in weights):
                    raise ValueError("All weights must be positive")
            random.seed(self.block_hash)
            result = random.choices(array, weights=weights, k=k)
            if len(result) == 1:
                return str(result[0])
            return result

        def shuffle(self, array: list = None) -> list:
            if array is None:
                array = [None]
            if not isinstance(array, list):
                raise TypeError("Array must be of type list")
            random.seed(self.block_hash)
            random.shuffle(array)
            return array

    class SlotFuncs:
        def __init__(self, block_hash: str, symbol_table: dict = None, grid: tuple = (5,5)) -> None:
            self.block_hash = block_hash

            if symbol_table is None:
                pass
            self.symbol_table = symbol_table
            self.grid = grid

        def get_reels(self) -> list[Any]:
            board = []
            symbols = []
            weights = []
            current_count = {}
            max_counts = {}
            for symbol in self.symbol_table.keys():
                symbols.append(symbol)
            for symbol in self.symbol_table:
                weights.append(self.symbol_table[symbol].get("weight"))
            for symbol in self.symbol_table:
                current_count[symbol] = 0
                max_counts[symbol] = self.symbol_table[symbol].get("max_count")
            if sum(max_counts.values()) < sum(self.grid):
                raise OverflowError("Ran out of symbols")
            for y in range(self.grid[1]):
                array = []
                for x in range(self.grid[0]):
                    result = GameTools.BasicFuncs(self.block_hash + str(x) + str(y)).get_choices(symbols, weights, 1)
                    array.append(result)
                    current_count[result] += 1
                    if current_count[result] == max_counts[result]:
                        weights.pop(symbols.index(result))
                        symbols.remove(result)
                        if len(symbols) == 0:
                            raise OverflowError("Ran out of symbols (caught late)")
                board.append(array)
            return board

        def get_symbol_odds(self) -> list:
            table = []
            symbols = []
            weights = []
            total_weight = 0
            for symbol in self.symbol_table.keys():
                symbols.append(symbol)
            for symbol in self.symbol_table:
                key = symbol_table[symbol].get("weight")
                total_weight += key
                weights.append(key)
            for symbol in symbols:
                table.append([symbol, f"{symbol_table[symbol].get('weight')} ({symbol_table[symbol].get('weight')/total_weight*100:.2f}%)"])
            return table

g = GameTools.BasicFuncs(hashlib.sha256(str(time.time()).encode()).hexdigest())


print(g.get_int(1,12))
print(g.get_choices([100,200,300], [1,2,300.1], 1))
print(g.shuffle([100,200,300]))

symbol_table = {
    "CHERRY": {
        "weight": 50,
        "max_count": 1000000
    },
    "BELL": {
        "weight": 30,
        "max_count": 1000000
    },
    "JACKPOT": {
        "weight": 1,
        "max_count": 100000
    }
}

start = time.time()
g = GameTools.SlotFuncs(hashlib.sha256(str(time.time()).encode()).hexdigest(), symbol_table=symbol_table, grid=(100, 100))
g.get_reels()
end = time.time()
print(end - start)

"""
EV = 0

for i in range(1000000000):
    block_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()
    EV += Dice(block_hash, random.choice(["under", "over"]), random.random()*100, 100)
    Expected = EV/(i+1)
    if i % 100000 == 0:
        print(f"{(i+1)/10000000:.2f}: {Expected}")
print(Expected, EV)

class Dice:
    def __init__(self, ammount):
        self.ammount = 0"""