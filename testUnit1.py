
NUM_TXS = 1_000_000      # total number of signatures to verify
NUM_WORKERS = cpu_count()

# --- Pre-generate a single key and signature to reuse ---
sk = SigningKey.generate()
vk = sk.verify_key
message = b"benchmark_message"
sig = sk.sign(message)

# Worker function: verify the same signature many times
def worker_verify(n):
    for _ in range(n):
        vk.verify(sig)
    return n

if __name__ == "__main__":
    # Split total TXs evenly across workers
    txs_per_worker = NUM_TXS // NUM_WORKERS + 1
    start = time.time()

    with Pool(NUM_WORKERS) as pool:
        results = pool.map(worker_verify, [txs_per_worker] * NUM_WORKERS)

    end = time.time()
    total_verified = sum(results)
    elapsed = end - start

    print(f"Total verifications: {total_verified}")
    print(f"Time taken with {NUM_WORKERS} processes: {elapsed:.4f}s")
    print(f"Throughput: {total_verified / elapsed:.0f} sigs/sec")
