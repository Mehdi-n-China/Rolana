import json

from tools import Singleton
import sqlite3
import time
from exceptions import *
from config.config import require_authority

class PeerManager(Singleton(1)):
    def __init__(self) -> None:
        self.conn = sqlite3.connect('../config/peers.db')
        self.pointer = self.conn.cursor()
        self.pointer.execute("PRAGMA synchronous = FULL")
        self.pointer.execute("""CREATE TABLE IF NOT EXISTS inbound
                             (peer_ip TEXT PRIMARY KEY,
                             peer_data TEXT)""")
        self.pointer.execute("""CREATE TABLE IF NOT EXISTS outbound
                             (peer_ip TEXT PRIMARY KEY,
                             peer_data TEXT)""")
        self.conn.commit()

        self._load_from_config()

    def _load_from_config(self) -> None:
        self.pointer.execute("SELECT * FROM inbound")
        inbound = self.pointer.fetchall()
        self.pointer.execute("SELECT * FROM outbound")
        outbound = self.pointer.fetchall()

        self.inbound: dict[str, object] = {
                        peer[0]: PeerContainer.from_string(peer[0], peer[1])
                        for peer
                        in inbound
                        }

        self.outbound: dict[str, object] = {
                        peer[0]: PeerContainer.from_string(peer[0], peer[1])
                        for peer
                        in outbound
                        }

    def add_peers(self, *,
                  inbound_peers: dict[str, object] = None,
                  outbound_peers: dict[str, object] = None) -> None:

        if inbound_peers:
            self.inbound.update({peer_ip: peer_data for peer_ip, peer_data in inbound_peers.items()})
            self.pointer.executemany("""
                                        INSERT INTO inbound (
                                            peer_ip,
                                            peer_data
                                        )
                                        VALUES (?, ?)
                                        ON CONFLICT(peer_ip)
                                        DO UPDATE SET
                                            peer_data = excluded.peer_data
                                        """,
                                        [
                                            (peer_ip, peer_data.to_string())
                                            for peer_ip, peer_data
                                            in inbound_peers.items()
                                        ]
                                    )

        if outbound_peers:
            self.outbound.update(outbound_peers)
            self.pointer.executemany("""
                                        INSERT INTO outbound (
                                            peer_ip,
                                            peer_data
                                        )
                                        VALUES (?, ?)
                                        ON CONFLICT(peer_ip)
                                        DO UPDATE SET
                                            peer_data = excluded.peer_data
                                        """,
                                        [
                                            (peer_ip, peer_data.to_string())
                                            for peer_ip, peer_data
                                            in outbound_peers.items()
                                        ]
                                    )

        self.conn.commit()

    def remove_peers(self, *,
                     inbound_peers: list[str] = None,
                     outbound_peers: list[str] = None) -> None:

        for peer in inbound_peers:
            self.inbound.pop(peer, None)
        self.pointer.executemany("""
                                    DELETE
                                    FROM inbound
                                    WHERE peer_ip = ?
                                    """,[
                                        (peer,) for peer in inbound_peers
                                    ]
                                 )

        for peer in outbound_peers:
            self.outbound.pop(peer, None)
        self.pointer.executemany("""
                                    DELETE
                                    FROM outbound
                                    WHERE peer_ip = ?
                                    """,[
                                        (peer,) for peer in inbound_peers
                                    ]
                                 )
        self.conn.commit()

class PeerContainer:
    def __init__(self, ip: str = "", port: int = 0, last_connection: int = 0,
                 banned_until: int = 0, handshake_status: int = 0,
                 trust_score: int = 0) -> None:

        self.ip: str = ip
        self.port: int = port
        self.last_connection: int = last_connection
        self.banned_until: int = banned_until
        self.handshake_status: int = handshake_status
        self.trust_score: int = trust_score

    @staticmethod
    def from_string(ip, data: bytes):
        return PeerContainer(ip, *json.loads(data))

    def to_string(self) -> str:
        return json.dumps([
            self.port,
            self.last_connection,
            self.banned_until,
            self.handshake_status,
            self.trust_score
        ])

    @property
    def is_banned(self) -> bool:
        return time.time() < self.banned_until

    def adjust_trust(self, adjustment: int) -> None:
        self.trust_score += adjustment
        if self.trust_score < 0:
            self.banned_until = (time.time()) + abs(self.trust_score)
            self.trust_score = 0

    def timeout(self, timeout: int | float, *, force_float: bool = False) -> None:
        if isinstance(timeout, float):
            if force_float:
                self.banned_until = time.time() + timeout
            else:
                raise ValueError("You must set force_float=True to use a float timeout.")
        elif isinstance(timeout, int):
            self.banned_until = time.time() + timeout
        else:
            raise TypeError(f"Invalid timeout value: {timeout}")

    @require_authority(1)
    def force_unban(self, trust_score: int = 0) -> None:
        self.banned_until = 0
        if not isinstance(trust_score, int) or trust_score < 0:
            self.trust_score = 0
        else:
            self.trust_score = trust_score

    def to_bytes(self) -> bytes:
        return b"".join([])

    def ping(self):
        pass



if __name__ == "__main__":
    t0 = time.time()
    p = PeerManager()

    peers = {f"127.0.0.{i}": PeerContainer(f"127.0.0.{i}", 6969, int(time.time()), 0, 0, 1_000_000) for i in range(1, 1000)}

    p.add_peers(inbound_peers=peers, outbound_peers=peers)
    p.remove_peers(inbound_peers=[peer for peer in peers], outbound_peers=[peer for peer in peers])
    t1 = time.time()
    print(t1 - t0)
    print(p.inbound)

