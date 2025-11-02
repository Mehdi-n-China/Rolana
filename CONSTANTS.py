"""
THIS IS THE BACKBONE OF MANY FUNCTIONS

DO NOT INTERACT WITH THIS BINARY, YOU WILL BREAK STUFF, THIS IS INTENDED FOR DEVELOPMENT ONLY

UNLESS YOU ARE FORKING THE COIN THIS IS NOT MEANT TO BE TOUCHED IN ANY WAY

if you NEED to pull from this file for DEV PURPOSES we recommend using INTERNAL FUNCTIONS directly
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class TX:
    TYPES: tuple = ("transfer", "bet", "swap")
    TRANSFER_REQUIREMENTS: tuple = ("to", "amount", "fee")
    BET_REQUIREMENTS: tuple = ("amount", "game", "params")
    SWAP_REQUIREMENTS: tuple = ("to", "amount", "fee")
    DELEGATE_REQUIREMENTS: tuple = ("to", "amount", "fee")

TX = TX()

@dataclass(frozen=True)
class BLOCK:
    MAX_TXS: int = 10000 # max txs allowed per block
    MAX_FILL_TIME: int = 0.5 # ms

BLOCK = BLOCK()

@dataclass(frozen=True)
class CONSENSUS:
    MAX_VALIDATORS: int = 69
    MIN_SIGNATURES: int = 46 # minimum consensus signatures required

CONSENSUS = CONSENSUS()

@dataclass(frozen=True)
class BASE_FEES:
    TRANSFER: int = 10000
    SWAP: int = 10000
    DELEGATE: int = 10000

BASE_FEES = BASE_FEES()

@dataclass(frozen=True)
class FEE_RATE:
    TRANSFER: int = 0.0001
    SWAP: int = 0.0001
    DELEGATE: int = 0.0001

FEE_RATE = FEE_RATE()

@dataclass(frozen=True)
class MINIMUMS:
    BALANCE: int = 1000000

@dataclass(frozen=True)
class NETWORK:
    MAX_SIZE_IN_BYTES = 1

@dataclass(frozen=True)
class PEER_TRUST_SCORE:
    MAX_SCORE: int = 1_000_000
    INITIAL_SCORE: int = 1_000_000

@dataclass(frozen=True)
class TRUST_SCORE_FLUCTUATION:
    VALID_TX: int = 1_000
    INVALID_TX: int = -10_000
    RECOVERY_RATE: float = 1

@dataclass(frozen=True)
class PEER_DB_FLUSH:
    INBOUND_ADDS: int = 100
    OUTBOUND_ADDS: int = 10
    INBOUND_REMOVALS: int = 100
    OUTBOUND_REMOVALS: int = 10