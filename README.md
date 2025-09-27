"""
data_carver.py

A multi-tool script to
 1. carve JPEG/PNG fragments from a raw image  
 2. scaffold a Python package for distribution  
 3. install a systemd unit for automatic/service-mode runs  
 
Usage:
  # 1) Carve fragments:
  ./data_carver.py carve /dev/sdx -o recovered/

  # 2) Scaffold a pip-installable package:
  ./data_carver.py init-package my_carver_pkg

  # 3) Generate & install a systemd service:
  sudo ./data_carver.py install-service \
      --device /dev/sdx \
      --output-dir /var/lib/data_carver/output \
      --user root
"""

import os
import sys
import argparse
import logging
from logging.handlers import RotatingFileHandler
from google.cloud import logging as gcloud_logging
from textwrap import dedent

# carving signatures
SIGNATURES = {
    'jpg': {'start': b'\xff\xd8\xff',       'end': b'\xff\xd9'},
    'png': {'start': b'\x89PNG\r\n\x1a\n',  'end': b'IEND\xaeB`\x82'}
}

# 1) logging setup
def setup_temp_logger(path="temp.log"):
    logger = logging.getLogger("temp")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger

def setup_main_logger():
    client = gcloud_logging.Client()
    client.setup_logging(log_level=logging.INFO)
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    return logger

# 2) carving logic
def carve_image(image_path, output_dir, temp_logger, main_logger):
    temp_logger.info(f"Starting carve on {image_path}")
    with open(image_path, 'rb') as f:
        data = f.read()
    for ext, sig in SIGNATURES.items():
        off = 0
        count = 0
        while True:
            start_idx = data.find(sig['start'], off)
            if start_idx == -1:
                temp_logger.info(f"No more {ext.upper()} headers after {off:#x}")
                break
            temp_logger.info(f"Found {ext.upper()} header at {start_idx:#x}")
            end_idx = data.find(sig['end'], start_idx)
            if end_idx < 0:
                temp_logger.warning(f"No {ext.upper()} end at {start_idx:#x}")
                break
            end_idx += len(sig['end'])
            fragment = data[start_idx:end_idx]
            os.makedirs(output_dir, exist_ok=True)
            fname = f"recovered_{ext}_{count}.{ext}"
            path = os.path.join(output_dir, fname)
            with open(path, 'wb') as out:
                out.write(fragment)
            main_logger.info(f"Recovered {fname} ({start_idx:#x}→{end_idx:#x}), size={len(fragment)}")
            temp_logger.info(f"Wrote fragment {fname}")
            count += 1
            off = end_idx
        if count == 0:
            temp_logger.info(f"No {ext.upper()} fragments found")
    temp_logger.info("Carve complete")

# 3) package scaffolding
def init_package(pkg_name):
    os.makedirs(f"{pkg_name}/{pkg_name}", exist_ok=True)
    with open(f"{pkg_name}/setup.py", 'w') as f:
        f.write(dedent(f"""
            from setuptools import setup, find_packages

            setup(
                name="{pkg_name}",
                version="0.1.0",
                packages=find_packages(),
                install_requires=["google-cloud-logging"],
                entry_points={{"console_scripts": ["carve={pkg_name}.main:main"]}}
            )
        """).strip())
    with open(f"{pkg_name}/README.md", 'w') as f:
        f.write(f"# {pkg_name}\n\nData carving utility with dual logging.")
    with open(f"{pkg_name}/{pkg_name}/__init__.py", 'w') as f:
        f.write("")
    with open(f"{pkg_name}/{pkg_name}/main.py", 'w') as f:
        f.write(dedent(f"""
            def main():
                print("Replace this with import carve logic.")
        """).strip())
    print(f"[OK] Scaffolded Python package at ./{pkg_name}/")

# 4) systemd service installer
SERVICE_TEMPLATE = """\
[Unit]
Description=Data Carver Service
After=network.target

[Service]
Type=simple
ExecStart={exec_path} carve {device} -o {output_dir}
User={user}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""

def install_service(exec_path, device, output_dir, user):
    unit = SERVICE_TEMPLATE.format(
        exec_path=exec_path, device=device,
        output_dir=output_dir, user=user
    )
    dest = "/etc/systemd/system/data-carver.service"
    with open(dest, 'w') as f:
        f.write(unit)
    os.system("systemctl daemon-reload")
    os.system("systemctl enable data-carver.service")
    print(f"[OK] Installed service unit to {dest}")

def main():
    p = argparse.ArgumentParser(prog="data_carver.py")
    subs = p.add_subparsers(dest="cmd", required=True)

    carve = subs.add_parser("carve", help="Run the carving routine")
    carve.add_argument("image", help="Raw image/device path")
    carve.add_argument("-o", "--output", default="recovered_files")

    pkg = subs.add_parser("init-package", help="Scaffold a Python package")
    pkg.add_argument("name", help="New package name")

    svc = subs.add_parser("install-service", help="Install systemd service")
    svc.add_argument("--device", required=True, help="/dev path to carve")
    svc.add_argument("--output-dir", required=True, help="Where to save fragments")
    svc.add_argument("--user", default="root", help="Run service as this user")

    args = p.parse_args()

    if args.cmd == "carve":
        temp_log = setup_temp_logger()
        main_log = setup_main_logger()
        carve_image(args.image, args.output, temp_log, main_log)

    elif args.cmd == "init-package":
        init_package(args.name)

    elif args.cmd == "install-service":
        install_service(
            exec_path=os.path.abspath(sys.argv[0]),
            device=args.device,
            output_dir=args.output_dir,
            user=args.user
        )

if __name__ == "__main__":
    main()
