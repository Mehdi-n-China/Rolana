# hybrid_node_template.py
import threading
import queue
import time
from multiprocessing import Process, Queue as MPQueue

# -------------------
# CPU-Heavy Validator Process
# -------------------
def validator_process(inbox: MPQueue, outbox: MPQueue):
    """CPU-heavy validation tasks live here."""
    while True:
        msg = inbox.get()
        if msg == "STOP":
            break

        if msg["type"] == "validate_block":
            block = msg["block"]
            # Simulate CPU-heavy validation
            time.sleep(1)
            validated_block = {"type": "validated_block", "block": block}
            outbox.put(validated_block)

        elif msg["type"] == "ask_example":
            # respond to ask-style message
            response = {"type": "response", "data": f"Response to {msg['question']}"}
            outbox.put(response)


# -------------------
# Thread-Based Components
# -------------------
class NetworkManager(threading.Thread):
    def __init__(self, validator_inbox: MPQueue):
        super().__init__(daemon=True)
        self.validator_inbox = validator_inbox

    def run(self):
        block_id = 1
        while True:
            time.sleep(2)
            print(f"[NetworkManager] Received Block#{block_id}")
            # Send to validator for CPU-heavy validation
            self.validator_inbox.put({"type": "validate_block", "block": f"Block#{block_id}"})
            block_id += 1


class ChainManager(threading.Thread):
    def __init__(self, validator_outbox: MPQueue):
        super().__init__(daemon=True)
        self.validator_outbox = validator_outbox

    def run(self):
        while True:
            msg = self.validator_outbox.get()
            if msg["type"] == "validated_block":
                print(f"[ChainManager] Block processed: {msg['block']}")
            elif msg["type"] == "response":
                print(f"[ChainManager] Got response: {msg['data']}")


# -------------------
# Main Node Entry
# -------------------
if __name__ == "__main__":
    # Multiprocessing queues for CPU-heavy validator
    validator_inbox = MPQueue()
    validator_outbox = MPQueue()

    # Start validator process
    validator = Process(target=validator_process, args=(validator_inbox, validator_outbox))
    validator.start()

    # Start thread-based main components
    network = NetworkManager(validator_inbox)
    chain = ChainManager(validator_outbox)
    network.start()
    chain.start()

    try:
        # Example of ask message
        time.sleep(5)
        validator_inbox.put({"type": "ask_example", "question": "What is the answer?"})

        # Keep main alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        validator_inbox.put("STOP")
        validator.join()
