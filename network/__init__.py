
from tools import *

import CONSTANTS

import json

class NetworkHandler:
    pass

class MessageHandler:
    @staticmethod
    def initial_verification(msg: json):
        try:
            msg = json.loads(msg)
            check_instance(msg, str)
            if len(msg) > 1:
                return False
            return True
        except WrongTypeError as e:
            return False


    @classmethod
    def handle_tx(cls, tx: dict, handl):
        pass

def main() -> None:
    MessageHandler.initial_verification(hi)

if __name__ == "__main__":
    main()
