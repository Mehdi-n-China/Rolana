from .BaseManager import BaseManager
import sqlite3
import json

class StateDBManager(BaseManager):
    def __init__(self, god_manager: object) -> None:
        super().__init__(god_manager)
        self.conn = sqlite3.connect("Databases/State.db", check_same_thread=False)
        self.pointer = self.conn.cursor()

        # SQLite performance + durability setup
        self.pointer.executescript("""
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = FULL;
        """)

        # Table setup
        self.pointer.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                pub_key TEXT PRIMARY KEY,
                data TEXT
            )
        """)

        self.pointer.execute("""
            CREATE TABLE IF NOT EXISTS globals (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)


        self.conn.commit()

    def _get(self, key: str):
        self.pointer.execute(
            "SELECT data FROM accounts WHERE pub_key = ?",
            (key,)
        )
        row = self.pointer.fetchone()
        return json.loads(row[0]) if row else None

    def _set(self, account_data: dict, global_data: dict) -> None:
        self.pointer.executemany(
            "INSERT INTO accounts (pub_key, data) VALUES (?, ?) "
            "ON CONFLICT(pub_key) DO UPDATE SET data = excluded.data",
            [(k, json.dumps(v)) for k, v in account_data.items()]
        )

        self.pointer.executemany(
            "INSERT INTO globals (key, data) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET data = excluded.data",
            [(k, v) for k, v in global_data.items()]
        )


        self.conn.commit()

    def _main(self):
        """Main loop to process queued messages."""
        while True:
            msgs = self.await_drain_inbox()
            for msg in msgs:
                self.handle_msg(msg)

    def handle_msg(self, msg: dict):
        """Route messages and reply appropriately."""
        match msg.get("cmd"):
            case "get":
                self.reply(msg, self._get(msg.get("key")))

            case "set":
                self._set(msg.get("type"), msg.get("data"))
