import gc
import json
import sys
import time
from tools import InstanceManager, Singleton
import exceptions
from collections import deque

class NetworkManager(Singleton(1)):
    pass

class PeerManager(Singleton(1)):
    def __init__(self) -> None:
        self.load_from_config()

    def load_from_config(self) -> None:
        with open("../config/peers.json", "r") as f:
            if f.read() == "":
                self.inbound, self.outbound = {}, {}

            f.seek(0)
            data = json.load(f)
            self.inbound, self.outbound = data.get("inbound_peers", {}), data.get("outbound_peers", {})

    @staticmethod
    def remove_from_config(*, inbound_peers: list = None, outbound_peers: list = None) -> None:
        global f
        try:
            f = open("../config/peers.json", "r")
            data = json.load(f)

            f = open("../config/peers.json", "w")
            if inbound_peers:
                for peer in inbound_peers:
                    data["inbound_peers"].pop(peer, None)

            if outbound_peers:
                for peer in outbound_peers:
                    data["outbound_peers"].pop(peer, None)

            json.dump(data, f)

        except FileNotFoundError:
            pass

        finally:
            if f:
                f.close()

    @staticmethod
    def push_to_config(*, new_inbound_peers: dict[str, str] = None,
                             new_outbound_peers: dict[str, str] = None) -> None:
        global f
        try:
            if new_inbound_peers is None and new_outbound_peers is None:
                raise exceptions.NoPeerProvidedError(__name__)

            if new_inbound_peers is None:
                new_inbound_peers = {}

            if new_outbound_peers is None:
                new_outbound_peers = {}

            f = open("../config/peers.json", "r")
            if f.read() == "":
                with open("../config/peers.json", "w") as f:
                    json.dump({"inbound_peers": {}, "outbound_peers": {}}, f)
                inbound_peers = {}
                outbound_peers = {}
                data = {"inbound_peers": {}, "outbound_peers": {}}

            else:
                f.seek(0)
                data = json.load(f)
                inbound_peers = data.get("inbound_peers", {})
                outbound_peers = data.get("outbound_peers", {})

            f = open("../config/peers.json", "w")
            data["inbound_peers"] = {**inbound_peers, **(new_inbound_peers or {})}
            data["outbound_apeers"] = {**outbound_peers, **(new_outbound_peers or {})}

            json.dump(data, f)

        except exceptions.NetworkError as e:
            print(e)

        finally:
            if f:
                f.close()


def main() -> None:
    p = PeerManager()
    p.load_from_config()
    p.kill()
    p.load_from_config()




if __name__ == "__main__":
    main()


