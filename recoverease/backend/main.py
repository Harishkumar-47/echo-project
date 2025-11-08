import os
from scanner.disk_scanner import list_logical_drives, read_raw_sectors
from scanner.signature_matcher import detect_file_signatures
from recovery.fragment_stitcher import extract_fragments, stitch_fragments
from recovery.file_writer import save_fragments
from utils.device_utils import is_admin
import scanner.scanner_config as config

def run_recovery(file_types=None, usb_only=False, preview=False, output_dir=None, verbose=False, dryrun=False):
    if not is_admin():
        print("❌ RecoverEase requires Administrator privileges to access raw disk sectors.")
        print("🔐 Please right-click your Command Prompt and choose 'Run as administrator'.")
        return []

    print("🔍 Available Drives:")
    drives = list_logical_drives()

    if usb_only:
        drives = [d for d in drives if not d.startswith("C")]
        print("🧷 USB-only mode: filtered drives")

    for d in drives:
        print(f" - {d}")

    choice = input("Enter drive letter to scan (e.g., E): ").upper()
    drive_path = f"{choice}:"

    try:
        raw_data = read_raw_sectors(drive_path, sector_size=512, num_sectors=20000)
    except Exception as e:
        print(f"❌ Failed to read raw sectors: {e}")
        return []

    if verbose:
        print(f"✅ Read {len(raw_data)} bytes from {drive_path}")

    try:
        with open(config.RAW_DUMP_FILE, "wb") as f:
            f.write(raw_data)
        if verbose:
            print(f"🧪 Raw dump saved to {config.RAW_DUMP_FILE}")
    except Exception as e:
        print(f"⚠️ Could not save raw dump: {e}")

    matches = detect_file_signatures(raw_data, file_types)
    if not matches:
        print("⚠️ No recognizable file fragments found.")
        return []

    print(f"🧩 Found {len(matches)} recoverable fragments:")
    for m in matches:
        print(f" - {m['type'].upper()} file from {m['start']} to {m['end']} ({m['size']} bytes)")

    fragments = extract_fragments(raw_data, matches)
    stitched = stitch_fragments(fragments)
    print(f"🧵 Stitched {len(stitched)} fragments from {len(fragments)} raw pieces")

    if preview:
        for i, frag in enumerate(stitched):
            print(f"\n🔍 Preview {i+1}: {frag['type'].upper()} ({frag['size']} bytes)")
            print(frag['data'][:64].hex())

    if dryrun:
        print("🧪 Dry run mode: stitched fragments not saved.")
    else:
        save_fragments(stitched, output_dir)

    return stitched

def run_folder_recovery(folder_path, file_types=None, preview=False, output_dir=None, verbose=False, dryrun=False):
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return []

    print(f"📂 Scanning folder: {folder_path}")
    fragments = []

    for root, _, files in os.walk(folder_path):
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "rb") as f:
                    data = f.read()
                matches = detect_file_signatures(data, file_types)
                if matches:
                    print(f"🧩 {fname}: Found {len(matches)} fragment(s)")
                    extracted = extract_fragments(data, matches)
                    fragments.extend(extracted)
                    if preview:
                        for i, frag in enumerate(extracted):
                            print(f"\n🔍 Preview {i+1}: {frag['type'].upper()} ({frag['size']} bytes)")
                            print(frag['data'][:64].hex())
            except Exception as e:
                print(f"⚠️ Could not read {fpath}: {e}")

    stitched = stitch_fragments(fragments)
    print(f"🧵 Stitched {len(stitched)} fragments from {len(fragments)} raw pieces")

    if preview:
        for i, frag in enumerate(stitched):
            print(f"\n🔍 Preview {i+1}: {frag['type'].upper()} ({frag['size']} bytes)")
            print(frag['data'][:64].hex())

    if dryrun:
        print("🧪 Dry run mode: stitched fragments not saved.")
    else:
        save_fragments(stitched, output_dir)

    return stitched
