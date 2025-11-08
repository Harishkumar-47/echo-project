import os
import msvcrt
import ctypes

def read_raw_sectors(drive_letter, sector_size=512, num_sectors=1000, verbose=True):
    path = f"\\\\.\\{drive_letter.strip(':')}:"
    GENERIC_READ = 0x80000000
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    OPEN_EXISTING = 3

    if verbose:
        print(f"🔍 Attempting raw read from {path} ({num_sectors * sector_size // 1024} KB)...")

    handle = ctypes.windll.kernel32.CreateFileW(
        path,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None
    )

    if handle == -1 or handle == 0:
        raise OSError(f"❌ Failed to open raw handle for {drive_letter}. Are you running as administrator?")

    try:
        os_handle = msvcrt.open_osfhandle(handle, os.O_RDONLY)
        with os.fdopen(os_handle, 'rb') as f:
            data = f.read(sector_size * num_sectors)
            if verbose:
                print(f"✅ Read {len(data)} bytes from {drive_letter}")
            return data
    except Exception as e:
        raise RuntimeError(f"❌ Raw read failed: {e}")



