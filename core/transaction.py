import hashlib

from core import _crypto
import json

from exceptions import WrongTypeError
from tools import check_instance

import CONSTANTS

class TransactionContainer:
    def __init__(self, identity: bytes, type: str, nonce: int, sig: bytes, **kwargs) -> None:
        self.isValid = False

        check_instance(identity, bytes, 32)
        self.identity = identity

        check_instance(type, str)
        if type not in CONSTANTS.TX.TYPES: raise WrongTypeError(f"'{type}' is not a valid transaction type! -> Valid types: {CONSTANTS.TX.TYPES}")
        self.type = type

        check_instance(nonce, int)
        self.nonce = nonce

        if type not in CONSTANTS.TX.TYPES:
            raise ValueError(f"Invalid tx type: {type}")

        self.to = to = kwargs.get("to")
        check_instance(to, bytes)

        self.amount = amount = kwargs.get("amount")
        check_instance(amount, int)

        self.fee = fee = kwargs.get("fee")
        check_instance(fee, int)
        if self.fee < 0:
            raise ValueError(f"Invalid fee value: {fee}")

        self.game = game = kwargs.get("game")
        check_instance(game, str)

        self.params = params = kwargs.get("params")
        check_instance(params, list)

        requiredFields = getattr(CONSTANTS.TX, f"{type.upper()}_REQUIREMENTS")
        missing = [field for field in requiredFields if getattr(self, field) is None]

        if missing:
            raise ValueError(f"Missing fields: {missing}")

        check_instance(sig, bytes, 64)
        self.sig = sig

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
                    }
                }, indent=4)

class TransactionHandler:
    isValid = False

    @classmethod
    def verifyTransaction(cls, tx: TransactionContainer) -> bool:
        try:
            if not tx.isValid:
                raise ValueError("transaction failed to initialize")

            if not crypto.validateSignature(tx.identity, tx.sig, tx.hash):
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


