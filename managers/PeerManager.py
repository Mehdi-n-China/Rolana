import json

from typing import Any
import sqlite3
import time
from exceptions import *
from Databases.config import require_authority
from managers.BaseManager import BaseManager
import CONSTANTS

class PeerManager(BaseManager):
    def __init__(self, god_manager) -> None:
        super().__init__(god_manager)

        self.conn = sqlite3.connect('Databases/peers.db', check_same_thread=False)
        self.pointer = self.conn.cursor()

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

        self._load_from_config()

        self.conn.close()

        self._dirty_adds_inbound = {}
        self._dirty_adds_outbound = {}
        self._dirty_removals_inbound = set()
        self._dirty_removals_outbound = set()
        self._needs_commit = False
        self._last_commit = time.perf_counter()

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

    def add_peers(
        self, *,
        inbound_peers: dict[str, object] = None,
        outbound_peers: dict[str, object] = None
    ) -> None:

        if inbound_peers:
            self.inbound.update(inbound_peers)
            self._dirty_removals_inbound.difference_update(inbound_peers.keys())
            self._dirty_adds_inbound.update(inbound_peers)
            if not self._needs_commit:
                if len(self._dirty_adds_inbound) > CONSTANTS.PEER_DB_FLUSH.INBOUND_ADDS:
                    self._needs_commit = True

        if outbound_peers:
            self.outbound.update(outbound_peers)
            self._dirty_removals_outbound.difference_update(outbound_peers.keys())
            self._dirty_adds_outbound.update(outbound_peers)
            if not self._needs_commit:
                if len(self._dirty_adds_outbound) > CONSTANTS.PEER_DB_FLUSH.OUTBOUND_ADDS:
                    self._needs_commit = True



        if self._needs_commit or time.perf_counter() - self._last_commit > 60:
            self._push_to_db()

    def remove_peers(self, *,
                     inbound_peers: list[str] = None,
                     outbound_peers: list[str] = None) -> None:

        for peer in inbound_peers:
            self.inbound.pop(peer, None)
            self._dirty_adds_inbound.pop(peer, None)
        self._dirty_removals_inbound.update(inbound_peers)
        if not self._needs_commit:
            if len(self._dirty_removals_inbound) > CONSTANTS.PEER_DB_FLUSH.INBOUND_REMOVALS:
                self._needs_commit = True

        for peer in outbound_peers:
            self.outbound.pop(peer, None)
            self._dirty_adds_outbound.pop(peer, None)
        self._dirty_removals_outbound.update(inbound_peers)
        if not self._needs_commit:
            if len(self._dirty_removals_inbound) > CONSTANTS.PEER_DB_FLUSH.OUTBOUND_REMOVALS:
                self._needs_commit = True

        if self._needs_commit or time.perf_counter() - self._last_commit > 60:
            self._push_to_db()


    def _push_to_db(self) -> None:
        self.send(
            "PeerDataBaseWriter",
            {
                "inbound_adds": self._dirty_adds_inbound,
                "outbound_adds": self._dirty_adds_outbound,
                "inbound_removals":self._dirty_removals_inbound,
                "outbound_removals": self._dirty_removals_outbound}
        )

        self._dirty_adds_inbound.clear()
        self._dirty_adds_outbound.clear()
        self._dirty_removals_inbound.clear()
        self._dirty_removals_outbound.clear()
        self._last_commit: float = time.perf_counter()

    def _main(self) -> None:
        while True:
            msgs = self.await_drain_inbox()
            for msg in msgs:
                self.handle_msg(msg)

    def handle_msg(self, msg: dict[str, Any]) -> None:
        match msg.get("cmd"):
            case "add":
                self.add_peers(inbound_peers=msg.get("inbound"),
                               outbound_peers=msg.get("outbound"))

            case "remove":
                self.remove_peers(inbound_peers=msg.get("inbound"),
                                  outbound_peers=msg.get("outbound"))

            case "inquire":
                match msg.get("mode", None):
                    case "inbound":
                        self.reply(msg, self.inbound)
                    case "outbound":
                        self.reply(msg, self.outbound)
                    case "all":
                        self.reply(msg, {"inbound": self.inbound, "outbound": self.outbound})

            case _:
                raise RuntimeError(f"Unhandled msg: {msg}")

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

    def to_string(self) -> json[str]:
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
    def force_unban(self, *, trust_score: int = 0) -> None:
        self.banned_until = 0
        if not isinstance(trust_score, int) or trust_score < 0:
            self.trust_score = 0
        else:
            self.trust_score = trust_score


