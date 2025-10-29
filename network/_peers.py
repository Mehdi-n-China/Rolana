
from tools import Singleton
import sqlite3
import time
from exceptions import *

class PeerManager(Singleton(1)):
    def __init__(self) -> None:
        self.conn = sqlite3.connect('../config/peers.db')
        self.pointer = self.conn.cursor()
        self.pointer.execute("PRAGMA synchronous = FULL")
        self.pointer.execute("""CREATE TABLE IF NOT EXISTS inbound
                             (peer_ip TEXT PRIMARY KEY,
                             peer_port INTEGER,
                             peer_last_connection INTEGER,
                             peer_allowed INTEGER,
                             peer_lives_left INTEGER)""")
        self.pointer.execute("""CREATE TABLE IF NOT EXISTS outbound
                             (peer_ip TEXT PRIMARY KEY,
                             peer_port INTEGER,
                             peer_last_connection INTEGER,
                             peer_allowed INTEGER,
                             peer_lives_left INTEGER)""")
        self.conn.commit()

        self._load_from_config()

    def _load_from_config(self) -> None:
        self.pointer.execute("SELECT * FROM inbound")
        inbound = self.pointer.fetchall()

        self.pointer.execute("SELECT * FROM outbound")
        outbound = self.pointer.fetchall()

        self.inbound = {peer[0]: [peer[1], peer[2], peer[3], peer[4]] for peer in inbound}
        self.outbound = {peer[0]: [peer[1], peer[2], peer[3], peer[4]] for peer in outbound}

    def add_peers(self, *, inbound_peers: dict[str, list[int]], outbound_peers: dict[str, list[int]]) -> None:
        if inbound_peers:
            self.inbound.update(inbound_peers)
            self.pointer.executemany("""
                                        INSERT INTO inbound (
                                            peer_ip,
                                            peer_port,
                                            peer_last_connection,
                                            peer_allowed,
                                            peer_lives_left
                                        )
                                        VALUES (?, ?, ?, ?, ?)
                                        ON CONFLICT(peer_ip)
                                        DO UPDATE SET
                                            peer_port = excluded.peer_port,
                                            peer_last_connection = excluded.peer_last_connection,
                                            peer_allowed = excluded.peer_allowed,
                                            peer_lives_left = excluded.peer_lives_left
                                        """,
                                        [
                                            (peer_ip, peer_port, peer_last_connection, peer_allowed, peer_lives_left)
                                            for peer_ip, peer_port, peer_last_connection, peer_allowed, peer_lives_left
                                            in inbound_peers.items()
                                        ]
                                    )

        if outbound_peers:
            self.outbound.update(outbound_peers)
            print(outbound_peers)
            self.pointer.executemany("""
                                        INSERT INTO outbound (
                                            peer_ip,
                                            peer_port,
                                            peer_last_connection,
                                            peer_allowed,
                                            peer_lives_left
                                        )
                                        VALUES (?, ?, ?, ?, ?)
                                        ON CONFLICT(peer_ip)
                                        DO UPDATE SET
                                            peer_port = excluded.peer_port,
                                            peer_last_connection = excluded.peer_last_connection,
                                            peer_allowed = excluded.peer_allowed,
                                            peer_lives_left = excluded.peer_lives_left
                                        """,
                                        [
                                            (peer_ip, peer_port, peer_last_connection, peer_allowed, peer_lives_left)
                                            for peer_ip, peer_port, peer_last_connection, peer_allowed, peer_lives_left
                                            in outbound_peers.items()
                                        ]
                                    )

        self.conn.commit()

    def remove_peers(self, *, inbound_peers: list, outbound_peers: list) -> None:
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

    def kick_peers(self, *, inbound_peers: dict, outbound_peers: dict) -> None:
        pass

class PeerContainer:
    def __init__(self, ip: str, port: int, last_connection: int, banned_until: int, handshake_status: int, trust_score: int) -> None:
        self.ip: str = ip
        self.port: int = port
        self.last_connection: int = last_connection
        self.banned_until: int = banned_until
        self.handshake_status: int = handshake_status
        self.trust_score: int = trust_score

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
    p = PeerManager()
    p.add_peers(inbound_peers={"hi": [5000, ]}, outbound_peers={})

