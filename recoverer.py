import os
import json
import re
import mmap
from PIL import Image
from typing import Optional, Dict, List

CHUNK_LOG_BYTES = 64 * 1024 * 1024
MAX_FILE_SIZE = 256 * 1024 * 1024
MIN_OFFSET_GAP = 1024
FOOTER_WINDOW = 32 * 1024 * 1024
FALLBACK_ON_NO_FOOTER = True
MIN_VALID_SIZE = 512

class Recoverer:
    def __init__(self, signature_file: str):
        self.signatures = self._load_signatures(signature_file)
        self.compiled = self._compile_signatures(self.signatures)

    def _load_signatures(self, path: str) -> Dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _compile_signatures(self, sigs: Dict) -> List[Dict]:
        compiled = []
        for name, spec in sigs.items():
            header = bytes.fromhex(spec["header"])
            footer = bytes.fromhex(spec["footer"]) if "footer" in spec else None
            ext = spec.get("extension", "").lower()
            max_size = int(spec.get("max_size", MAX_FILE_SIZE))
            compiled.append({
                "name": name,
                "extension": ext,
                "header": header,
                "footer": footer,
                "max_size": max_size
            })
        return compiled

    def _matches_type(self, file_type: Optional[str], sig: Dict) -> bool:
        if not file_type:
            return False
        ft = file_type.lower().strip().lstrip(".")
        return ft == sig["extension"] or ft == sig["name"].lower()

    def _safe_write(self, base_dir: str, name: str, data: bytes) -> str:
        os.makedirs(base_dir, exist_ok=True)
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
        out_path = os.path.abspath(os.path.join(base_dir, safe_name))
        if not out_path.startswith(os.path.abspath(base_dir) + os.sep):
            raise ValueError("Unsafe output path attempt")
        with open(out_path, "wb") as f:
            f.write(data)
        return out_path

    def is_valid_image(self, path: str) -> bool:
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except Exception:
            return False

    def detect_format(self, data: bytes) -> str:
        if data.startswith(b'\xff\xd8\xff'):
            return "jpg"
        elif data.startswith(b'\x89PNG'):
            return "png"
        elif data.startswith(b'RIFF') and b'WEBP' in data:
            return "webp"
        return "bin"

    def scan_device(self, device_path: str, output_dir: str, file_type: Optional[str] = None) -> List[Dict]:
        results = []
        seen_offsets: List[int] = []
        fd = open(device_path, "rb")
        try:
            try:
                filesize = os.fstat(fd.fileno()).st_size
                mm = mmap.mmap(fd.fileno(), length=0, access=mmap.ACCESS_READ)
                use_mmap = True
            except:
                mm = None
                use_mmap = False

            if use_mmap:
                results = self._scan_mmap(mm, filesize, file_type, output_dir, seen_offsets)
            else:
                results = self._scan_stream(fd, file_type, output_dir, seen_offsets)
        finally:
            if mm: mm.close()
            fd.close()
        return results

    def _scan_mmap(self, mm: mmap.mmap, filesize: int, file_type: Optional[str], output_dir: str, seen_offsets: List[int]) -> List[Dict]:
        results = []
        pos = 0
        while pos < filesize:
            for sig in self.compiled:
                if not self._matches_type(file_type, sig):
                    continue
                header = sig["header"]
                idx = mm.find(header, pos, min(pos + CHUNK_LOG_BYTES, filesize))
                while idx != -1:
                    try:
                        if any(abs(idx - s) < MIN_OFFSET_GAP for s in seen_offsets):
                            idx = mm.find(header, idx + len(header), min(pos + CHUNK_LOG_BYTES, filesize))
                            continue
                        seen_offsets.append(idx)

                        data = (
                            self._carve_with_footer_mmap(mm, idx, header, sig["footer"], sig["max_size"], filesize)
                            if sig.get("footer")
                            else self._carve_fixed_mmap(mm, idx, header, sig["max_size"], filesize)
                        )

                        if not data or len(data) < MIN_VALID_SIZE:
                            idx = mm.find(header, idx + len(header), min(pos + CHUNK_LOG_BYTES, filesize))
                            continue

                        ext = self.detect_format(data) if sig["extension"] in ["jpg", "png", "webp"] else sig["extension"]
                        name = f"recovered_{sig['name']}_{idx}.{ext}"
                        path = self._safe_write(output_dir, name, data)

                        if ext in ["jpg", "png", "webp"] and not self.is_valid_image(path):
                            print(f"[warn] Skipping corrupt image: {path}")
                            idx = mm.find(header, idx + len(header), min(pos + CHUNK_LOG_BYTES, filesize))
                            continue

                        print(f"[write] {name} -> {path} ({len(data)} bytes)")
                        results.append({"path": path, "type": sig["name"], "size": len(data), "offset": idx})
                    except Exception as e:
                        print(f"[error] Failed at offset {idx}: {e}")
                    idx = mm.find(header, idx + len(header), min(pos + CHUNK_LOG_BYTES, filesize))
            pos += CHUNK_LOG_BYTES
        return results

    def _scan_stream(self, fd, file_type: Optional[str], output_dir: str, seen_offsets: List[int]) -> List[Dict]:
        results = []
        buffer = b""
        offset = 0
        while True:
            chunk = fd.read(CHUNK_LOG_BYTES)
            if not chunk:
                break
            buffer += chunk
            for sig in self.compiled:
                if not self._matches_type(file_type, sig):
                    continue
                header = sig["header"]
                search_pos = 0
                while True:
                    idx = buffer.find(header, search_pos)
                    if idx == -1:
                        break
                    abs_offset = offset + idx
                    try:
                        if any(abs(abs_offset - s) < MIN_OFFSET_GAP for s in seen_offsets):
                            search_pos = idx + len(header)
                            continue
                        seen_offsets.append(abs_offset)

                        data = (
                            self._read_until_footer_stream(fd, buffer, idx, header, sig["footer"], sig["max_size"])
                            if sig.get("footer")
                            else self._read_fixed_stream(fd, buffer, idx, header, sig["max_size"])
                        )

                        if not data or len(data) < MIN_VALID_SIZE:
                            search_pos = idx + len(header)
                            continue

                        ext = self.detect_format(data) if sig["extension"] in ["jpg", "png", "webp"] else sig["extension"]
                        name = f"recovered_{sig['name']}_{abs_offset}.{ext}"
                        path = self._safe_write(output_dir, name, data)

                        if ext in ["jpg", "png", "webp"] and not self.is_valid_image(path):
                            print(f"[warn] Skipping corrupt image: {path}")
                            search_pos = idx + len(header)
                            continue

                        print(f"[write] {name} -> {path} ({len(data)} bytes)")
                        results.append({"path": path, "type": sig["name"], "size": len(data), "offset": abs_offset})
                    except Exception as e:
                        print(f"[error] Failed at offset {abs_offset}: {e}")
                    search_pos = idx + len(header)
            if len(buffer) > FOOTER_WINDOW:
                buffer = buffer[-FOOTER_WINDOW:]
            offset += len(chunk)
        return results

    def _carve_with_footer_mmap(self, mm: mmap.mmap, start: int, header: bytes, footer: bytes, max_size: int, end: int) -> Optional[bytes]:
        search_end = min(start + FOOTER_WINDOW, end, start + max_size)
        fidx = mm.find(footer, start + len(header), search_end)
        if fidx != -1:
            return mm[start:fidx + len(footer)]
        return mm[start:min(start + max_size, end)] if FALLBACK_ON_NO_FOOTER else None

    def _carve_fixed_mmap(self, mm: mmap.mmap, start: int, header: bytes, max_size: int, end: int) -> Optional[bytes]:
        return mm[start:min(start + max_size, end)]

    def _read_until_footer_stream(self, fd, buffer: bytes, start_idx: int, header: bytes, footer: bytes, max_size: int) -> Optional[bytes]:
        data = buffer[start_idx:]
        fidx = data.find(footer, len(header))
        if fidx != -1:
            return data[:fidx + len(footer)]

        total = bytes(data)
        to_read = min(FOOTER_WINDOW, max_size) - len(total)
        while to_read > 0:
            more = fd.read(min(to_read, 4 * 1024 * 1024))
            if not more:
                break
            total += more
            to_read -= len(more)
            fidx = total.find(footer, len(header))
            if fidx != -1:
                return total[:fidx + len(footer)]

        return total[:min(len(total), max_size)] if FALLBACK_ON_NO_FOOTER else None

    def _read_fixed_stream(self, fd, buffer: bytes, start_idx: int, header: bytes, max_size: int) -> Optional[bytes]:
        data = buffer[start_idx:]
        if len(data) >= max_size:
            return data[:max_size]

        pieces = [data]
        need = max_size - len(data)
        while need > 0:
            more = fd.read(min(4 * 1024 * 1024, need))
            if not more:
                break
            pieces.append(more)
            need -= len(more)

        return b"".join(pieces)[:max_size]
