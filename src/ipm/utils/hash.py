from pathlib import Path
import hashlib


def ifp_hash(lfp_path: str | Path, block_size=65536) -> bytes:
    sha256 = hashlib.sha256()
    with Path(lfp_path).resolve().open("rb") as file:
        for block in iter(lambda: file.read(block_size), b""):
            sha256.update(block)
    return sha256.digest()


def ifp_verify(lfp_path, expected_hash) -> bool:
    actual_hash = ifp_hash(lfp_path)
    return actual_hash == expected_hash
