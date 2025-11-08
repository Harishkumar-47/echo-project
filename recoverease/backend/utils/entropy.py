import math

def entropy(data: bytes) -> float:
    """
    Calculates Shannon entropy of a byte sequence.
    """
    if not data:
        return 0.0

    freq = [0] * 256
    for b in data:
        freq[b] += 1

    total = len(data)
    ent = 0.0
    for count in freq:
        if count:
            p = count / total
            ent -= p * math.log2(p)
    return ent
