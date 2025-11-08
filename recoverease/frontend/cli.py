import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
from backend.main import run_recovery, run_folder_recovery

parser = argparse.ArgumentParser(description="RecoverEase CLI")

parser.add_argument('--scan', action='store_true', help='Scan raw drive sectors')
parser.add_argument('--folder', type=str, help='Scan a folder for recoverable fragments')
parser.add_argument('--type', type=str, help='Comma-separated file types to recover (e.g., jpg,pdf)')
parser.add_argument('--usb', action='store_true', help='Scan only external USB drives')
parser.add_argument('--preview', action='store_true', help='Preview fragments before saving')
parser.add_argument('--output', type=str, help='Custom output directory')
parser.add_argument('--verbose', action='store_true', help='Enable detailed logging')
parser.add_argument('--dryrun', action='store_true', help='Simulate recovery without saving files')

args = parser.parse_args()
file_types = args.type.split(',') if args.type else None

if args.folder:
    run_folder_recovery(
        folder_path=args.folder,
        file_types=file_types,
        preview=args.preview,
        output_dir=args.output,
        verbose=args.verbose,
        dryrun=args.dryrun
    )
elif args.scan:
    run_recovery(
        file_types=file_types,
        usb_only=args.usb,
        preview=args.preview,
        output_dir=args.output,
        verbose=args.verbose,
        dryrun=args.dryrun
    )
