import os
import msvcrt
import ctypes
from scanner.signature_matcher import match_signatures

GENERIC_READ = 0x80000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_NO_BUFFERING = 0x20000000
FILE_FLAG_RANDOM_ACCESS = 0x10000000

def open_raw_handle(drive_letter="D"):
    path = f"\\\\.\\{drive_letter.strip(':')}:"
    handle = ctypes.windll.kernel32.CreateFileW(
        path,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_NO_BUFFERING | FILE_FLAG_RANDOM_ACCESS,
        None
    )
    if handle in (0, -1):
        raise OSError(f"Failed to open raw handle for {drive_letter}. Run as Administrator.")
    return handle

def read_chunks(drive_letter="D", sector_size=512, chunk_sectors=100, max_bytes=None, verbose=True):
    """
    Read the volume in fixed-size chunks.
    """
    handle = open_raw_handle(drive_letter)
    os_handle = msvcrt.open_osfhandle(handle, os.O_RDONLY)
    total = 0
    chunk_size = sector_size * chunk_sectors
    try:
        with os.fdopen(os_handle, 'rb') as f:
            i = 0
            while True:
                if max_bytes is not None and total >= max_bytes:
                    break
                data = f.read(chunk_size)
                if not data:
                    break
                i += 1
                total += len(data)
                if verbose and i % 50 == 0:
                    print(f"✅ Read {i} chunks, total {total // 1024} KB")
                yield data
    except Exception as e:
        raise RuntimeError(f"Raw read failed: {e}")

def recover_files(drive_letter="D", output_dir="recovered", sector_size=512, chunk_sectors=100,
                  max_bytes=None, file_types=None, fragment_size=1024 * 500, verbose=True):
    """
    Full recovery pipeline:
    - Streams the drive in chunks
    - Detects signatures and carves fragments
    - Saves files into output_dir
    """
    os.makedirs(output_dir, exist_ok=True)
    file_count = 0

    for idx, chunk in enumerate(read_chunks(drive_letter, sector_size, chunk_sectors, max_bytes, verbose)):
        hits = match_signatures(chunk, file_types=file_types, fragment_size=fragment_size)
        for fname, content in hits:
            out_path = os.path.join(output_dir, f"{idx}_{fname}")
            try:
                with open(out_path, "wb") as out_f:
                    out_f.write(content)
                file_count += 1
                if verbose:
                    print(f"💾 Saved {out_path} ({len(content)} bytes)")
            except Exception as e:
                if verbose:
                    print(f"⚠️ Could not save {out_path}: {e}")

    if verbose:
        print(f"🎉 Recovery complete: {file_count} files saved to {output_dir}")
    return file_count

