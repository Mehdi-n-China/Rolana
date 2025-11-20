
import threading
import time
import datetime
from managers import *
import random

from managers.PeerManager import PeerContainer

class NetworkManager(BaseManager):
    def _main(self):
        while True:
            t0 = time.perf_counter()
            for i in range(10000):
                lucky = random.randint(1, 1_000_000)
                self.send("Mem", {"cmd": "add", "inbound": {f"peer_{lucky}": PeerContainer(f"peer{lucky}", lucky, lucky, lucky, lucky, lucky)}})
                resp = self.send_with_response("PeerManager", {"cmd": "inquire", "mode": "all"})
            t1 = time.perf_counter()
            print(f"Network manager took {t1 - t0} seconds")
            break
            time.sleep(1)

class GodManager:
    def __init__(self):
        self.registry: dict[str, BaseManager] = {}
        self.block_manager: BlockManager = BlockManager(self)
        self.mempool_manager: MempoolManager = MempoolManager(self)
        self.network_manager: NetworkManager = NetworkManager(self)
        self.peer_db_writer: PeerDataBaseWriter = PeerDataBaseWriter(self)
        self.peer_manager: PeerManager = PeerManager(self)
        self.state_manager: StateManager = StateManager(self)

    def register(self, manager):
        self.registry[manager.__class__.__name__] = manager

    def start(self):
        for manager in self.__dict__.values():
            if isinstance(manager, BaseManager):
                print("starting {}".format(manager))
                threading.Thread(target=manager.start, daemon=True).start()

    def stop(self):
        for manager in self.__dict__.values():
            if isinstance(manager, BaseManager):
                manager.stop()

    def route(self, target_name, msg):
        target = self.registry.get(target_name)
        if target:
            target.inbox.put(msg)


def main() -> None:
    Node = GodManager()
    Node.start()
    while True:
        time.sleep(42069)

if __name__ == '__main__':
    main()