import socket
import threading
import queue

class NetworkManager(threading.Thread):
    def __init__(self, peer_manager: PeerManager):
        super().__init__(daemon=True)
        self.peer_manager = peer_manager
        self.inbox = queue.Queue()
        self.outbox = queue.Queue()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 8333))  # example port
        self.server_socket.listen(5)

    def run(self):
        # Start thread to accept inbound connections
        threading.Thread(target=self.accept_inbound, daemon=True).start()
        # Start thread to manage outbound connections
        threading.Thread(target=self.connect_outbound, daemon=True).start()
        # Process inbox/outbox messages
        while True:
            self.process_messages()

    def accept_inbound(self):
        while True:
            client_sock, addr = self.server_socket.accept()
            peer_id = f"{addr[0]}:{addr[1]}"
            print(f"[NetworkManager] Inbound connection from {peer_id}")
            self.peer_manager.add_peers(inbound_peers={peer_id: addr[0]})
            threading.Thread(target=self.handle_peer, args=(client_sock, peer_id), daemon=True).start()

    def connect_outbound(self):
        while True:
            for peer_id, ip in self.peer_manager.outbound.items():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((ip, 8333))
                    print(f"[NetworkManager] Connected to outbound peer {peer_id}")
                    threading.Thread(target=self.handle_peer, args=(sock, peer_id), daemon=True).start()
                except Exception:
                    pass
            time.sleep(5)

    def handle_peer(self, sock: socket.socket, peer_id: str):
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                self.inbox.put((peer_id, data))
            except Exception:
                break
        print(f"[NetworkManager] Disconnected {peer_id}")
        sock.close()
        self.peer_manager.remove_peers(inbound_peers=[peer_id], outbound_peers=[])

    def process_messages(self):
        while not self.inbox.empty():
            peer_id, data = self.inbox.get()
            print(f"[NetworkManager] Received from {peer_id}: {data}")
            # TODO: decode and dispatch messages
