
import hashlib

from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError

def get_signable_text(identity: bytes = None, type: str = None, nonce: int = None, to: bytes = None, amount: int = None, fee: int = None,
                 game: str = None,
      params: list = None) -> str:
    return hashlib.sha256(
            str(identity.hex()+
                type+
                str(nonce)+
                to.hex()+
                str(amount)+
                str(fee)+
                game+
                str(params))
            .encode()).hexdigest()

def sign_message(privateKey: bytes, message: str) -> bytes:
    """Sign a message using Ed25519, returns hex string"""
    try:
        signingKey = SigningKey(privateKey)
        return bytes(signingKey.sign(message.encode()))[:64]
    except Exception as e:
        raise e

def validate_signature(publicKey: bytes, signature: bytes, message: str) -> bool:
    try:
        verifyKey = VerifyKey(publicKey)
        verifyKey.verify(message.encode(), signature)
        return True
    except BadSignatureError:
        return False

def make_key_pair() -> tuple[bytes, bytes]:
    sk = SigningKey.generate()
    pk = sk.verify_key

    return sk.encode(), pk.encode()
