
import json
import exceptions

def load_peers_from_config():
    with open("../config/peers.json", "r") as f:
        data = json.load(f)
        inbound_peers = data.get("inbound_peers", [])
        outbound_peers = data.get("outbound_peers", [])
        return inbound_peers, outbound_peers

def remove_peers(*, inbound_peers: list = None, outbound_peers: list = None) -> None:
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

def push_peers_to_config(*, new_inbound_peers: dict[str, str] = None,
                         new_outbound_peers: dict[str, str] = None) -> None:
    global f
    try:
        if new_inbound_peers is None and new_outbound_peers is None:
            raise exceptions.NoPeerProvidedError(__name__)

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
    remove_peers(inbound_peers=["1"])
    push_peers_to_config(new_inbound_peers={"1":"1", "2":"2", "3":"3", "4":"4", "5":"5"})

if __name__ == "__main__":
    main()
