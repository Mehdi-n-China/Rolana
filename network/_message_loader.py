
import threading
from queue import Queue

from network._peers import PeerManager

class MessageManager:
    def __init__(self, PeerManager: PeerManager):
        self.peer_manager = PeerManager
        self.inbox = Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)


    def start(self):
        self.thread.start()

    def _run(self):
        while True:
            peer_id, msg = self.inbox.get()
            try:
                msg_type = self._validate_and_classify(msg)
                self._dispatch(peer_id, msg_type, msg)
            except Exception as e:
                print(f"[WARN] Dropped bad message from {peer_id}: {e}")

    def _validate_and_classify(self, msg: dict):
        raise NotImplementedError()

    def _validate_block(self):
        if

    def _dispatch(self, peer_id, msg_type, msg):
        if msg_type == "tx":
            self.tx_manager.queue.put((peer_id, msg))
        elif msg_type == "block":
            self.block_manager.queue.put((peer_id, msg))
        elif msg_type == "consensus":
            self.consensus_manager.queue.put((peer_id, msg))
        else:
            print(f"[DROP] Unknown msg type from {peer_id}: {msg_type}")
