import gc
import json
import sys
import time
from tools import InstanceManager, Singleton
import exceptions
import sqlite3


class NetworkManager(Singleton(1)):
    pass

class PeerManager(Singleton(1)):
    def __init__(self) -> None:
        self.conn = sqlite3.connect('../config/peers.db')
        self.pointer = self.conn.cursor()
        self.pointer.execute("PRAGMA synchronous = FULL")
        self.pointer.execute("CREATE TABLE IF NOT EXISTS inbound_peers (peer_id TEXT PRIMARY KEY, peer_ip TEXT)")
        self.pointer.execute("CREATE TABLE IF NOT EXISTS outbound_peers (peer_id TEXT PRIMARY KEY, peer_ip TEXT)")
        self.conn.commit()

        self._load_from_config()

    def _load_from_config(self) -> None:
        self.pointer.execute("SELECT * FROM inbound_peers")
        inbound = self.pointer.fetchall()

        self.pointer.execute("SELECT * FROM outbound_peers")
        outbound = self.pointer.fetchall()

        self.inbound = {peer[0]: peer[1] for peer in inbound}
        self.outbound = {peer[0]: peer[1] for peer in outbound}

    def add_peers(self, *, inbound_peers: dict, outbound_peers: dict) -> None:
        if inbound_peers:
            self.inbound.update(inbound_peers)
            self.pointer.executemany("""INSERT INTO inbound_peers (peer_id, peer_ip)
                                        VALUES (?, ?)
                                        ON CONFLICT(peer_id) DO UPDATE SET peer_ip = excluded.peer_ip""",
                                     [(peer_id, peer_ip)
                                      for peer_id, peer_ip
                                      in inbound_peers.items()])

        if outbound_peers:
            self.outbound.update(outbound_peers)
            self.pointer.executemany("""INSERT INTO outbound_peers (peer_id, peer_ip)
                                        VALUES (?, ?)
                                        ON CONFLICT(peer_id) DO UPDATE SET peer_ip = excluded.peer_ip""",
                                     [(peer_id, peer_ip)
                                      for peer_id, peer_ip
                                      in outbound_peers.items()])

        self.conn.commit()

    def remove_peers(self, *, inbound_peers: list | dict, outbound_peers: list | dict) -> None:
        for peer in inbound_peers:
            self.inbound.pop(peer, None)
        self.pointer.executemany("""DELETE
                                        FROM inbound_peers
                                        WHERE peer_id = ?""",
                                 [(peer,) for peer in inbound_peers])

        for peer in outbound_peers:
            self.outbound.pop(peer, None)
        self.pointer.executemany("""DELETE
                                        FROM outbound_peers
                                        WHERE peer_id = ?""",
                                 [(peer,) for peer in outbound_peers])
        self.conn.commit()

def main() -> None:
    import random

    p = PeerManager()
    inbound_peers = {str(random.randint(1, 1_000_000)): str(random.randint(1, 1_000_000)) for i in range(1000)}
    inbound_peers_2 = [str(random.randint(1, 1_000_000)) for i in range(1000)]
    start = time.perf_counter()
    p.add_peers(inbound_peers=inbound_peers, outbound_peers=inbound_peers)
    p.remove_peers(inbound_peers=inbound_peers_2, outbound_peers=inbound_peers_2)
    stop = time.perf_counter()

    print(stop - start)
    print(len(p.inbound))
    p.kill()




if __name__ == "__main__":
    main()


