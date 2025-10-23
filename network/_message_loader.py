
import asyncio
import json

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    print(f"[server] connection from {peer}")
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
                received = json.loads(text)
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

