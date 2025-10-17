
"""
Base62 encoder/decoder using alphabet 0-9, A-Z, a-z.

encode(data: str) -> str
    Converts a hex string into a Base62 string.
decode(data: str) -> str
    Converts a Base62 string back into a hex string.
"""

import hashlib

class Base62:
    ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    BASE = 62

    @classmethod
    def encode(cls, data: str) -> str:
        dataSum = cls.addChecksum(data)
        n = int(dataSum, 16)
        if n == 0:
            return cls.ALPHABET[0]
        chars = []
        while n > 0:
            n, rem = divmod(n, cls.BASE)
            chars.append(cls.ALPHABET[rem])
        return "".join(reversed(chars))

    @classmethod
    def decode(cls, data: str) -> str:
        n = 0
        for char in data:
            n = n * cls.BASE + cls.ALPHABET.index(char)
        hexKey = hex(n)[2:].lower()
        if cls.verifyChecksum(hexKey):
            return hexKey[:-5]
        else:
            raise Exception(f"Invalid chechsum: {hexKey}")

    @staticmethod
    def addChecksum(hexData: str) -> str:
        checksum = hashlib.sha1(bytes(hexData.encode())).hexdigest()[:5]
        return hexData + checksum

    @staticmethod
    def verifyChecksum(hex_data: str):
        data, checksum_found = hex_data[:-5], hex_data[-5:]
        return checksum_found == hashlib.sha1(bytes(data.encode())).hexdigest()[:5]

class PackBytes:
    ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789{}[]:,\"'-. "

    @classmethod
    def encode(cls, data: str) -> bytes:
        bitData = []
        for c in data:
            index = cls.ALPHABET.index(c)
            bitData.append(bin(index)[2:].zfill(6))
        bitString = "".join(bitData)

        byteLen = (len(bitString) + 7) // 8
        n = int(bitString, 2)

        return n.to_bytes(byteLen, "big")

    @classmethod
    def decode(cls, byteData: bytes) -> str:

        n = int.from_bytes(byteData, "big")

        bitData = bin(n)[2:]

        if len(bitData) % 6:
            bitData = bitData.zfill(((len(bitData) // 6) + 1) * 6)

        result = []
        for i in range(0, len(bitData), 6):
            chunk = bitData[i:i + 6]
            index = int(chunk, 2)
            result.append(cls.ALPHABET[index])

        return "".join(result)




