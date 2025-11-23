import os
import platform

def ensure_temp_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def resolve_device_path(raw_path):
    if platform.system() == "Windows":
        return raw_path
    return raw_path

def is_admin():
    try:
        return os.geteuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
