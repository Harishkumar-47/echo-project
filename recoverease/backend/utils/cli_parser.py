import argparse

def get_cli_args():
    parser = argparse.ArgumentParser(description="RecoverEase: Forensic File Recovery")

    parser.add_argument('--force-recover-small', action='store_true', help='Override size thresholds for all types')
    parser.add_argument('--usb-only', action='store_true', help='Scan only removable drives')
    parser.add_argument('--preview', action='store_true', help='Show hex preview of fragments')
    parser.add_argument('--dryrun', action='store_true', help='Scan but do not save files')
    parser.add_argument('--output-dir', type=str, default=None, help='Custom output folder for recovered files')
    parser.add_argument('--folder', type=str, help='Run recovery on a folder instead of a drive')
    parser.add_argument('--verbose', action='store_true', help='Enable detailed logging')

    return parser.parse_args()
