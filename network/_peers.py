
from tools import Singleton
import sqlite3

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


if __name__ == "__main__":
    p = PeerManager()
    p.add_peers(inbound_peers={}, outbound_peers={})

