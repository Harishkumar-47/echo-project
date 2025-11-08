def detect_file_signatures(data, file_types=None):
    signatures = {
        b"\xFF\xD8\xFF": "jpg",
        b"\x25\x50\x44\x46": "pdf",
        b"\x50\x4B\x03\x04": "zip",
        b"\x00\x00\x00\x18\x66\x74\x79\x70": "mp4"
    }

    fragments = []
    for sig, ext in signatures.items():
        index = data.find(sig)
        if index != -1:
            fragment = data[index:index + 1024 * 100]  # 100KB fragment
            fragments.append((ext, fragment))
    return fragments


