
from typing import Any
from .BaseManager import BaseManager
import sqlite3
import time

class PeerDataBaseWriter(BaseManager):
    def __init__(self, god_manager) -> None:
        super().__init__(god_manager)

        self._last_commit = time.perf_counter()

    def start(self):
        self.conn = sqlite3.connect('config/peers.db', check_same_thread=False)
        self.pointer = self.conn.cursor()

        self.pointer.executescript("""
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = FULL;
            PRAGMA cache_size = 0;
        """)

        self.pointer.execute("""
            CREATE TABLE IF NOT EXISTS inbound
            (peer_ip TEXT PRIMARY KEY,
            peer_data TEXT)
        """)

        self.pointer.execute("""
            CREATE TABLE IF NOT EXISTS outbound
            (peer_ip TEXT PRIMARY KEY,
            peer_data TEXT)
        """)

        self.conn.commit()

        super().start()

    def _main(self):
        while True:
            msgs = self.await_drain_inbox()

            msg = {
                "inbound_adds": {},
                "outbound_adds": {},
                "inbound_removals": set(),
                "outbound_removals": set()
            }

            for data in msgs:
                msg["inbound_adds"].update(data.get("inbound_adds", {}))
                msg["outbound_adds"].update(data.get("outbound_adds", {}))

                msg["inbound_removals"].update(data.get("inbound_removals", set()))
                msg["outbound_removals"].update(data.get("outbound_removals", set()))

            self._push_to_db(msg["inbound_adds"], msg["outbound_adds"],
                            msg["inbound_removals"], msg["outbound_removals"])

    def _push_to_db(self,
            inbound_adds: dict[str, Any],
            outbound_adds: dict[str, Any],
            inbound_removals: set[str],
            outbound_removals: set[str]
        ) -> None:

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
                (peer_ip, peer.to_string())
                for peer_ip, peer
                in inbound_adds.items()
            ]
        )

        self.pointer.executemany("""
            INSERT INTO outbound (
                peer_ip,
                peer_data
            )
            VALUES (?, ?)
            ON CONFLICT(peer_ip)
            DO UPDATE SET
                peer_data = excluded.peer_data
            """, [
                (peer_ip, peer.to_string())
                for peer_ip, peer
                in outbound_adds.items()
            ]
        )

        self.pointer.executemany("""
            DELETE
            FROM inbound
            WHERE peer_ip = ?
            """,[
                (peer,) for peer in inbound_removals
            ]
        )

        self.pointer.executemany("""
            DELETE
            FROM outbound
            WHERE peer_ip = ?
            """,
            [
                (peer,) for peer in outbound_removals
            ]
        )

        self.conn.commit()

        self._last_commit: float = time.perf_counter()
