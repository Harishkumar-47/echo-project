from recoverease.backend.scanner.scanner_config import ENTROPY_THRESHOLD
from recoverease.backend.recovery.file_writer import entropy, is_valid_jpeg, is_valid_pdf

def extract_fragments(raw_data: bytes, matches: list) -> list:
    fragments = []
    for match in matches:
        start = match["start"]
        end = match["end"]
        frag_data = raw_data[start:end]
        frag_type = match["type"]
        size = len(frag_data)
        ent = entropy(frag_data)
        print(f"🧪 Checking: {frag_type}, size={size}, entropy={ent:.2f}")
        if ent < ENTROPY_THRESHOLD:
            continue

        if frag_type == "jpg" and not is_valid_jpeg(frag_data):
            continue
        if frag_type == "pdf" and not is_valid_pdf(frag_data):
            continue

        fragments.append({
            "type": frag_type,
            "data": frag_data,
            "size": size,
            "entropy": ent,
            "deleted": True  # assume deleted for raw scan
        })
    return fragments

def stitch_fragments(fragments: list) -> list:
    return fragments  # placeholder for future stitching logic


