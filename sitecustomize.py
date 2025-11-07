import time
from nacl.signing import SigningKey
from multiprocessing import Pool, cpu_count

# optional: put them in builtins so you don’t even need to reference modules
import builtins
builtins.SigningKey = SigningKey
builtins.Pool = Pool
builtins.cpu_count = cpu_count
builtins.time = time