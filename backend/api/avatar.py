import hashlib


def avatar_indices(seed: str) -> tuple[int, int]:
    """Return stable avatar indexes. The values are stored and never recalculated."""
    digest = hashlib.sha256(seed.strip().lower().encode("utf-8")).digest()
    return digest[0] % 16 + 1, digest[1] % 9 + 1

