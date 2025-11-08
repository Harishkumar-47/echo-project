from scanner.disk_scanner import list_logical_drives, read_raw_sectors
from scanner.signature_matcher import detect_file_signatures
from recovery.file_writer import save_fragments, save_raw_fallback
from utils.win_toast import show_toast

def run_recovery(file_types=None, usb_only=False, preview=False, output_dir="recovered", verbose=True, dryrun=False, drive=None):
    if not drive:
        drives = list_logical_drives(usb_only=usb_only)
        if not drives:
            show_toast("❌ No drives found")
            return []
        drive = drives[0]

    try:
        raw_data = read_raw_sectors(drive, verbose=verbose)
    except OSError as e:
        show_toast(f"❌ {str(e)}")
        return []

    fragments = detect_file_signatures(raw_data, file_types=file_types)

    if preview:
        return fragments

    if fragments:
        save_fragments(fragments, output_dir, dryrun=dryrun)
    else:
        save_raw_fallback(raw_data, output_dir)

    show_toast("✅ Recovery complete")
    return fragments






