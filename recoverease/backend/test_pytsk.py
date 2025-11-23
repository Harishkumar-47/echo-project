import pytsk3

def list_root(drive="D"):
    # Open the logical volume
    img = pytsk3.Img_Info(rf"\\.\{drive}:")
    fs = pytsk3.FS_Info(img)

    print("Filesystem type:", fs.info.ftype)

    # List root directory entries
    directory = fs.open_dir(path="/")
    for entry in directory:
        name = entry.info.name.name.decode("utf-8", errors="ignore")
        if name not in [".", ".."]:
            print("File:", name)
            if entry.info.meta:
                print("  Size:", entry.info.meta.size)
                print("  Inode:", entry.info.meta.addr)

if __name__ == "__main__":
    list_root("D")
