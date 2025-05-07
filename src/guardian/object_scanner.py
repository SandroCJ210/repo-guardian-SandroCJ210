import zlib
from pathlib import Path
from hashlib import sha1
from dataclasses import dataclass

@dataclass
class GitObject:
    type: str
    size: int
    content: bytes
    sha: str

def read_loose(obj_path: Path) -> GitObject:
    if not obj_path.is_file():
        raise FileNotFoundError(f"Object file not found: {obj_path}")

    with obj_path.open("rb") as f:
        compressed = f.read()

    try:
        decompressed = zlib.decompress(compressed)
    except zlib.error as e:
        raise ValueError(f"Decompression failed: {e}")

    header_end = decompressed.find(b'\x00')
    if header_end == -1:
        raise ValueError("Missing null separator in object header")

    header = decompressed[:header_end].decode(errors="replace")
    body = decompressed[header_end + 1:]

    try:
        obj_type, size_str = header.split(" ")
        size = int(size_str)
    except ValueError:
        raise ValueError(f"Invalid header format: {header}")

    if size != len(body):
        raise ValueError(f"Declared size {size} does not match body size {len(body)}")

    full_obj = f"{obj_type} {size}".encode() + b"\x00" + body
    sha = sha1(full_obj, usedforsecurity=False).hexdigest()

    expected_sha = obj_path.parent.name + obj_path.name
    if sha[:len(expected_sha)] != expected_sha:
        raise ValueError(f"SHA mismatch: expected {expected_sha}, got {sha}")

    return GitObject(type=obj_type, size=size, content=body, sha=sha)

def read_packfile(pack_path: Path) -> list[GitObject]:
    MIN_HEADER_SIZE = 12  

    if not pack_path.is_file():
        raise FileNotFoundError(f"Packfile not found: {pack_path}")

    with pack_path.open("rb") as f:
        data = f.read()

    if len(data) < MIN_HEADER_SIZE:
        raise ValueError("Packfile too short — possibly truncated")

    if data[:4] != b"PACK":
        raise ValueError("Invalid packfile magic bytes (expected 'PACK')")

    version = int.from_bytes(data[4:8], "big")
    count = int.from_bytes(data[8:12], "big")

    if version not in {2, 3}:
        raise ValueError(f"Unsupported packfile version: {version}")


    return [GitObject("unknown", 0, b"", f"dummy-{i}") for i in range(count)]

