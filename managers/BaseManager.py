
import queue
from typing import Any
import os
from collections import deque

class BaseManager:
    def __init__(self, god_manager):
        self.god_manager: GodManager = god_manager
        self.inbox: queue.SimpleQueue = queue.SimpleQueue()
        self._response_queue: queue.SimpleQueue = queue.SimpleQueue()
        self.is_alive: bool = True
        self.god_manager.register(self)

    def start(self):
        self._main()

    def _main(self):
        raise NotImplementedError()

    def stop(self):
        self.is_alive = False

    def send(self, target, msg) -> None:
        self.god_manager.route(target, msg)

    def send_with_response(self, target, msg):
        msg["_resp_q"] = self._response_queue
        self.god_manager.route(target, msg)

        return self._response_queue.get()

    def reply(self, msg, data):
        msg["_resp_q"].put(data)

    def check_inbox(self) -> dict[str, Any] | None:
        try:
            return self.inbox.get_nowait()
        except queue.Empty:
            return None

    def await_inbox(self) -> dict[str, Any]:
        return self.inbox.get()

    def await_drain_inbox(self) -> list[dict[str, Any]] | None:
        items = [self.inbox.get()]
        while True:
            try:
                items.append(self.inbox.get_nowait())
            except queue.Empty:
                break
        return items

