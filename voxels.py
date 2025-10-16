import sqlite3
import time
import os
import gc

DB_FILE = "benchmark.db"
NUM_ROWS = 100_000
BATCH_SIZE = 100_000

SYNC_MODES = ["OFF", "NORMAL", "FULL"]
WAL_MODES = [False, True]
STRATEGIES = ["single", "transaction", "executemany"]

def generate_rows(n):
    return [(f"id_{i}", f"value_{i}") for i in range(n)]

rows = generate_rows(NUM_ROWS)
results = []

for wal in WAL_MODES:
    for sync in SYNC_MODES:
        for strategy in STRATEGIES:
            # Clean slate
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            gc.collect()  # free memory

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE accounts(account_id TEXT PRIMARY KEY, data TEXT)")

            cursor.execute(f"PRAGMA journal_mode={'WAL' if wal else 'DELETE'}")
            cursor.execute(f"PRAGMA synchronous={sync}")

            print(f"\nStarting test: Strategy={strategy}, Synchronous={sync}, WAL={wal}")
            start_time = time.time()

            if strategy == "single":
                for i, row in enumerate(rows, 1):
                    cursor.execute("INSERT INTO accounts(account_id, data) VALUES (?, ?)", row)
                    conn.commit()
                    if i % 1_000 == 0:
                        print(f"Inserted {i}/{NUM_ROWS}")

            elif strategy == "transaction":
                for batch_start in range(0, NUM_ROWS, BATCH_SIZE):
                    batch = rows[batch_start: batch_start + BATCH_SIZE]
                    cursor.execute("BEGIN TRANSACTION")
                    for row in batch:
                        cursor.execute("INSERT INTO accounts(account_id, data) VALUES (?, ?)", row)
                    cursor.execute("COMMIT")
                    print(f"Transaction committed {min(batch_start + BATCH_SIZE, NUM_ROWS)}/{NUM_ROWS}")

            elif strategy == "executemany":
                for batch_start in range(0, NUM_ROWS, BATCH_SIZE):
                    batch = rows[batch_start: batch_start + BATCH_SIZE]
                    cursor.execute("BEGIN TRANSACTION")
                    cursor.executemany("INSERT INTO accounts(account_id, data) VALUES (?, ?)", batch)
                    cursor.execute("COMMIT")
                    print(f"Executemany committed {min(batch_start + BATCH_SIZE, NUM_ROWS)}/{NUM_ROWS}")

            end_time = time.time()
            elapsed = end_time - start_time
            print(f"Completed test in {elapsed} seconds")

            results.append((strategy, sync, wal, elapsed))
            conn.close()

# Print final summary table
print("\n=== Benchmark Summary (seconds) ===")
print(f"{'Strategy':<12} {'Sync':<8} {'WAL':<5} {'Time (s)':<10}")
print("-" * 40)
for strategy, sync, wal, elapsed in results:
    print(f"{strategy:<12} {sync:<8} {str(wal):<5} {elapsed:<10.4f}")

time.sleep(10**6)