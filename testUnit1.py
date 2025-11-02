import time
from collections import OrderedDict
import random

N = 10_000_000  # number of items
iterations = 10000

# Prefill dict and OrderedDict
print("filling plain dict")
d_plain = {i: i for i in range(N)}
print("filling ordered dict")
d_ordered = OrderedDict((i, i) for i in range(N))

# Warm-up
print("warming up")
d_temp = dict(d_plain)
for _ in range(10):
    del d_temp[next(iter(d_temp))]

# Benchmark plain dict
dict_times = []
d_temp = dict(d_plain)
removals = random.sample(list(range(N)), k=iterations)
for _ in range(iterations):
    start = time.perf_counter()
    del d_temp[removals[_]]
    dict_times.append(time.perf_counter() - start)

# Benchmark OrderedDict
ordered_times = []
d_temp = OrderedDict(d_ordered)
for _ in range(iterations):
    start = time.perf_counter()
    d_temp.popitem(last=False)
    ordered_times.append(time.perf_counter() - start)

print("Average next(iter(d)) + del (dict):", sum(dict_times)/iterations)
print("Average popitem(last=False) (OrderedDict):", sum(ordered_times)/iterations)
