# simulate_network.py
import asyncio
import json
import random
import time
import unicodedata
from typing import Any, List, Tuple

def print(msg):
    with open("network_log.log", "a") as f:
        f.write(msg + "\n")

# -------------------------
# Canonical JSON serializer
# -------------------------
def normalize_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, list):
        return [normalize_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {normalize_obj(k): normalize_obj(v) for k, v in obj.items()}
    return obj

def canonical_json_bytes(obj: Any) -> bytes:
    normalized = normalize_obj(obj)
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

# -------------------------
# Reference validator
# -------------------------
def reference_validator(tx: dict) -> (bool, str):
    if not isinstance(tx, dict):
        return False, "not_a_object"
    required = {
        "sender": str, "receiver": str, "amount": (int,), "nonce": (int,), "timestamp": (int,float)
    }
    for k, t in required.items():
        if k not in tx:
            return False, f"missing_{k}"
        if not isinstance(tx[k], t):
            return False, f"bad_type_{k}"
    for name in ("sender","receiver"):
        try:
            tx[name].encode("ascii")
        except UnicodeEncodeError:
            return False, f"non_ascii_in_{name}"
    if tx["amount"] < 0 or tx["amount"] > 10**18:
        return False, "amount_out_of_range"
    if tx["nonce"] < 0 or tx["nonce"] > 2**63:
        return False, "nonce_out_of_range"
    if tx["timestamp"] - time.time() > 60:
        return False, "timestamp_in_future"
    return True, "ok"

# -------------------------
# Server logic with propagation
# -------------------------
class Server:
    def __init__(self, host: str, port: int, peers: List[Tuple[str,int]]):
        self.host = host
        self.port = port
        self.peers = peers
        self.mempool = set()  # store canonical TXs

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"[server {self.port}] listening on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        peer_addr = writer.get_extra_info("peername")
        while True:
            try:
                line = await reader.readline()
                if not line:
                    break
                raw = line.rstrip(b"\n\r")
                try:
                    tx = json.loads(raw.decode("utf-8"))
                except Exception:
                    print(f"[server {self.port}] GARBAGE from {peer_addr}")
                    continue
                await self.process_tx(tx)
            except Exception as e:
                break
        writer.close()
        await writer.wait_closed()

    async def process_tx(self, tx: dict):
        canonical = canonical_json_bytes(tx)
        if canonical in self.mempool:
            return
        is_valid, reason = reference_validator(tx)
        if is_valid:
            print(f"[server {self.port}] VALID TX: {tx}")
            self.mempool.add(canonical)
            asyncio.create_task(self.propagate(tx))
        else:
            print(f"[server {self.port}] INVALID TX ({reason}): {tx}")

    async def propagate(self, tx: dict):
        await asyncio.sleep(random.uniform(0.2, 1.5))
        for host, port in self.peers:
            try:
                reader, writer = await asyncio.open_connection(host, port)
                writer.write(canonical_json_bytes(tx)+b"\n")
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except Exception:
                continue

# -------------------------
# Infinite slow clients
# -------------------------
async def good_tx(sender: str, receiver: str, nonce: int):
    return {"sender": sender,"receiver": receiver,"amount": random.randint(1,10**6),"nonce":nonce,"timestamp": time.time()}

async def client_simulator(host: str, port: int, client_id: int):
    nonce = 0
    while True:
        nonce += 1
        choice = random.random()
        if choice < 0.7:
            tx = await good_tx(f"Client{client_id}", f"Dest{random.randint(1,5)}", nonce)
            payload = canonical_json_bytes(tx)+b"\n"
        else:
            payload = b'{"garbage":"oh no"}\n'
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.write(payload)
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            print(f"[client {client_id}] sent {'valid' if choice<0.7 else 'garbage'}")
        except Exception:
            pass
        await asyncio.sleep(1)  # 1 tx per second

# -------------------------
# Orchestrator
# -------------------------
async def run_simulation():
    servers = [
        Server("127.0.0.1", i, [("127.0.0.1", k) for k in range(num_server) if k != i])
        for i in range(num_server)
    ]

    server_tasks = [asyncio.create_task(s.start()) for s in servers]

    client_tasks = [
        asyncio.create_task(client_simulator("127.0.0.1", random.choice([i for i in range(num_server)]), i))
        for i in range(num_clients)
    ]

    await asyncio.gather(*server_tasks, *client_tasks)

if __name__ == "__main__":
    num_server = 10
    num_clients = 100
    asyncio.run(run_simulation())
