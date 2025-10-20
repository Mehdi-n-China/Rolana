
from core import *
from tools import *
import asyncio
import json
import random
import time
import unicodedata
from typing import Any

def normalize_obj(obj: Any) -> Any:
    """Recursively normalize strings (NFC) and ensure deterministic ordering for dicts."""
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, list):
        return [normalize_obj(x) for x in obj]
    if isinstance(obj, dict):
        # Note: keys are assumed to be strings; normalize them too
        return {normalize_obj(k): normalize_obj(v) for k, v in obj.items()}
    return obj
def canonical_json_bytes(obj: Any) -> bytes:
    """
    Serialize object to canonical JSON bytes:
     - normalize Unicode (NFC)
     - sort keys
     - no extra spaces (separators(',',':'))
     - ensure_ascii=False to keep UTF-8
    """
    normalized = normalize_obj(obj)
    return json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    print(f"[server] connection from {peer}")
    # We'll read newline-delimited messages; messages may be garbage, binary, etc.
    while True:
        try:
            line = await reader.readline()
            if not line:
                break  # connection closed
            # simulate receiving raw bytes
            raw = line.rstrip(b"\n\r")
            # Try decode as UTF-8; if fails, it's garbage/binary
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                print(f"[server] GARBAGE (non-utf8) from {peer} -- {raw[:60]!r}")
                continue

            # Sometimes multiple JSON objects were concatenated without newline.
            # Attempt to parse as a single JSON; if that fails, try to split by '}{' as a naive attempt.
            parsed_something = False
            try:
                obj = json.loads(text)
                parsed_something = True
                await process_message(obj, raw, peer)
            except json.JSONDecodeError:
                # Try naive split attempts
                chunks = try_split_jsons(text)
                if len(chunks) == 1:
                    print(f"[server] GARBAGE (malformed_json) from {peer} -- {text[:80]!r}")
                else:
                    for chunk in chunks:
                        try:
                            obj = json.loads(chunk)
                            await process_message(obj, chunk.encode("utf-8"), peer)
                        except Exception as e:
                            print(f"[server] GARBAGE (chunk_bad) from {peer} -- {chunk[:80]!r} -- {e}")
        except asyncio.IncompleteReadError:
            break
        except Exception as exc:
            print(f"[server] Exception while reading from {peer}: {exc}")
            break

    writer.close()
    await writer.wait_closed()
    print(f"[server] connection closed {peer}")
async def process_message(obj: Any, raw_bytes: bytes, peer):
    # Normalize strings (NFC) and prepare canonical bytes
    if isinstance(obj, (dict, list, str, int, float)):
        try:
            canonical = canonical_json_bytes(obj)
        except Exception as e:
            print(f"[server] GARBAGE (cannot_canonicalize) from {peer} -- {e}")
            return
    else:
        print(f"[server] GARBAGE (unsupported_json_type) from {peer} -- {type(obj)}")
        return

    # Now check that the top-level object is a tx (dict) and validate
    if isinstance(obj, dict):
        is_valid, reason = reference_validator(obj)
        if is_valid:
            print(f"[server] VALID from {peer}: {obj}")
            # If you want: push into mempool, hash, sign, whatever.
        else:
            print(f"[server] GARBAGE (validation_failed:{reason}) from {peer}: {obj}")
    else:
        print(f"[server] GARBAGE (not_object) from {peer}: {obj}")
def try_split_jsons(text: str):
    """
    Naive attempt to split concatenated JSON objects like:
      '{"a":1}{"b":2}' -> ['{"a":1}', '{"b":2}']
    Not perfect, but useful for simulation.
    """
    out = []
    depth = 0
    start = 0
    in_str = False
    escape = False
    for i, ch in enumerate(text):
        if ch == '"' and not escape:
            in_str = not in_str
        if in_str and ch == "\\" and not escape:
            escape = True
            continue
        if escape:
            escape = False
            continue
        if not in_str:
            if ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
        if depth == 0 and not in_str:
            # end of an object/array
            out.append(text[start:i+1])
            start = i+1
    # if nothing split, return original text as single chunk
    return out if len(out) > 1 else [text]

async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 5555)
    async with server:
        await server.serve_forever()

asyncio.run(main())

def main() -> None:
    sk, pk = make_key_pair()
    sig = sign_message(sk, get_signable_text(pk, "bet", 1, to=sk, amount=100, fee=100, game="100", params=["arg", "arg", "arg"]))

    start = time.time()
    for i in range(10000):
        tx = TransactionContainer(pk, "bet", 1, sig, to=sk, amount=100, fee=100, game="100", params=["arg", "arg", "arg"])

        validate_signature(tx.identity, tx.sig, tx.hash)
    end = time.time()
    print("Verification time:", end - start, "seconds")

if __name__ == "__main__":
    main()
