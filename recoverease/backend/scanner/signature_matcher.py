import hashlib

# Header → Footer pairs for precise carving
FOOTER_SIGS = {
    b"\xff\xd8\xff": (b"\xff\xd9", "jpg"),          # JPEG SOI → EOI
    b"%PDF": (b"%%EOF", "pdf"),                     # PDF start → EOF
    b"\x89PNG\r\n\x1a\n": (b"IEND\xaeB\x82", "png"),# PNG start → IEND
    b"PK\x03\x04": (b"PK\x05\x06", "zip"),          # ZIP start → End of central directory
}

# Fixed-size carving for formats without clear footer markers
FIXED_SIGS = {
    b"\x00\x00\x00\x18ftypmp42": "mp4",
    b"\x00\x00\x00 ftypisom": "mp4",
    b"\x00\x00\x00\x1cftyp3gp": "mp4",
    b"\x00\x00\x00\x14ftypM4V": "mp4",
    b"\x00\x00\x00\x1cftypMSNV": "mp4",
}

def detect_file_signatures(data, file_types=None, fragment_size=1024 * 500):
    """
    Detects file signatures in raw data.
    - Uses footer-aware carving for JPG, PDF, PNG, ZIP
    - Uses fixed-size carving for MP4
    - Deduplicates by MD5 hash
    Returns list of (filename, bytes).
    """
    seen_hashes = set()
    results = []

    # Footer-aware carving
    for header, (footer, ext) in FOOTER_SIGS.items():
        if file_types and ext not in file_types:
            continue
        start = data.find(header)
        while start != -1:
            end = data.find(footer, start + len(header))
            if end != -1:
                fragment = data[start:end + len(footer)]
            else:
                fragment = data[start:start + fragment_size]
            h = hashlib.md5(fragment).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                filename = f"{ext}_{h[:8]}.{ext}"
                results.append((filename, fragment))
            start = data.find(header, start + 1)

    # Fixed-size carving
    for sig, ext in FIXED_SIGS.items():
        if file_types and ext not in file_types:
            continue
        start = data.find(sig)
        while start != -1:
            fragment = data[start:start + fragment_size]
            h = hashlib.md5(fragment).hexdigest()
            if h not in seen_hashes:
                seen_hashes.add(h)
                filename = f"{ext}_{h[:8]}.{ext}"
                results.append((filename, fragment))
            start = data.find(sig, start + 1)

    return results

# Alias for disk_scanner integration
def match_signatures(data, file_types=None, fragment_size=1024 * 500):
    return detect_file_signatures(data, file_types=file_types, fragment_size=fragment_size)



