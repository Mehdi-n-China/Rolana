import hashlib


from Keys import Keys
from Tools import *
import json


import CONSTANTS

class TransactionContainer:
    def __init__(self, identity: bytes, type: str, nonce: int, sig: bytes, **kwargs) -> None:
        self.isValid = False

        checkInstance(identity, bytes, 32)
        self.identity = identity

        checkInstance(type, str)
        if type not in CONSTANTS.TX.TYPES: raise TypeError(f"'{type}' is not a valid transaction type! -> Valid types: {CONSTANTS.TX.TYPES}")
        self.type = type

        checkInstance(nonce, int)
        self.nonce = nonce

        if type not in CONSTANTS.TX.TYPES:
            raise ValueError(f"Invalid tx type: {type}")

        self.to = to = kwargs.get("to")
        checkInstance(to, bytes)

        self.amount = amount = kwargs.get("amount")
        checkInstance(amount, int)

        self.fee = fee = kwargs.get("fee")
        checkInstance(fee, int)
        if self.fee < 0:
            raise ValueError(f"Invalid fee value: {fee}")

        self.game = game = kwargs.get("game")
        checkInstance(game, str)

        self.params = params = kwargs.get("params")
        checkInstance(params, list)

        requiredFields = getattr(CONSTANTS.TX, f"{type.upper()}_REQUIREMENTS")
        missing = [field for field in requiredFields if getattr(self, field) is None]

        if missing:
            raise ValueError(f"Missing fields: {missing}")

        checkInstance(sig, bytes, 64)
        self.sig = sig

        self.hash = hashlib.sha256(
            str(self.identity.hex()+
                self.type+
                str(self.nonce)+
                self.to.hex()+
                str(self.amount)+
                str(self.fee)+
                self.game+
                str(self.params))
            .encode()).hexdigest()

        self.isValid = True

    def __str__(self) -> str:
        return json.dumps({
                    "message": {
                        "identity": self.identity.hex(),
                        "type": self.type,
                        "nonce": self.nonce,
                        "to": self.to.hex(),
                        "amount": self.amount,
                        "game": self.game,
                        "params": self.params
                    },
                    "cryptography": {
                        "sig": self.sig.hex(),
                        "hash": self.hash
                    }
                }, indent=4)

class TransactionHandler:
    isValid = False

    @classmethod
    def verifyTransaction(cls, tx: TransactionContainer) -> bool:
        try:
            if not tx.isValid:
                raise ValueError("transaction failed to initialize")

            if not Keys.validateSignature(tx.identity, tx.sig, tx.hash):
                raise ValueError("signature failed to validate")

            if tx.type == "transfer":
                if cls.validateTransfer(tx):
                    cls.isValid = True

            if cls.isValid:
                return True


        except Exception as e:
            raiseError(e)
            return False

    @staticmethod
    def validateTransfer(tx: "TransactionContainer") -> bool:
        try:
            if GlobalState.getNonce(tx.identity) >= tx.nonce:
                raise ValueError("Nonce is invalid")

            if GlobalState.getBalance(tx.identity) <= tx.amount + max(CONSTANTS.BASE_FEES.TRANSFER, int(tx.amount * CONSTANTS.FEE_RATE.TRANSFER)) +  tx.fee:
                raise ValueError(f"Transfer cost is too high")

            return True
        except Exception as e:
            return False

    @staticmethod
    def validateBet(tx: "TransactionContainer") -> bool:
        try:
            if GlobalState.getNonce(tx.identity) >= tx.nonce:
                raise ValueError("Nonce is invalid")

            if GlobalState.getBalance(tx.identity) <= tx.amount:
                raise ValueError("Balance is too low")

            return True
        except Exception as e:
            return False


