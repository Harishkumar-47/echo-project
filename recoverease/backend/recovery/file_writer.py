import os

def save_fragments(fragments, output_dir, dryrun=False):
    os.makedirs(output_dir, exist_ok=True)
    for i, (ext, data) in enumerate(fragments):
        if dryrun:
            continue
        with open(os.path.join(output_dir, f"{ext}_fragment_{i+1}.{ext}"), "wb") as f:
            f.write(data)

def save_raw_fallback(data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "bin_fragment_1.bin"), "wb") as f:
        f.write(data)




