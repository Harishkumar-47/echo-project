import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, subprocess
from scanner.disk_scanner import recover_files

# Try importing pytsk3 safely
try:
    import pytsk3
    HAS_PYTSK = True
except ImportError:
    HAS_PYTSK = False

def start_raw_recovery():
    drive = drive_var.get()
    if not drive:
        messagebox.showwarning("RecoverEase", "Please select a drive first!")
        return
    log_area.insert(tk.END, f"🔍 Starting RAW carving on {drive}...\n")
    log_area.see(tk.END)

    try:
        count = recover_files(
            drive_letter=drive,
            output_dir="recovered",
            file_types=["jpg", "png", "pdf", "mp4", "zip"],
            fragment_size=1024 * 500,
            verbose=True
        )
        log_area.insert(tk.END, f"🎉 RAW recovery complete: {count} files saved\n")
        log_area.see(tk.END)
        subprocess.Popen(f'explorer "{os.path.abspath("recovered")}"')
    except Exception as e:
        log_area.insert(tk.END, f"❌ Error: {e}\n")

def start_fs_recovery():
    if not HAS_PYTSK:
        messagebox.showerror("RecoverEase", "pytsk3 is not installed. Filesystem recovery unavailable.")
        return

    # Ask user to select a disk image file
    img_path = filedialog.askopenfilename(
        title="Select Disk Image",
        filetypes=[("Disk Images", "*.img *.dd *.raw"), ("All files", "*.*")]
    )
    if not img_path:
        return

    log_area.insert(tk.END, f"📂 Starting filesystem recovery on {img_path}...\n")
    log_area.see(tk.END)

    try:
        img = pytsk3.Img_Info(img_path)
        fs = pytsk3.FS_Info(img)

        recovered_dir = "fs_recovered"
        os.makedirs(recovered_dir, exist_ok=True)

        directory = fs.open_dir(path="/")
        count = 0
        for entry in directory:
            name = entry.info.name.name.decode("utf-8", errors="ignore")
            if name not in [".", ".."] and entry.info.meta and entry.info.meta.size > 0:
                out_path = os.path.join(recovered_dir, name)
                try:
                    file_obj = fs.open(name)
                    with open(out_path, "wb") as out_f:
                        offset = 0
                        size = file_obj.info.meta.size
                        while offset < size:
                            available = min(1024*1024, size - offset)
                            data = file_obj.read_random(offset, available)
                            if not data:
                                break
                            out_f.write(data)
                            offset += len(data)
                    count += 1
                    log_area.insert(tk.END, f"💾 Extracted {name}\n")
                    log_area.see(tk.END)
                except Exception as e:
                    log_area.insert(tk.END, f"⚠️ Could not recover {name}: {e}\n")

        log_area.insert(tk.END, f"🎉 Filesystem recovery complete: {count} files saved\n")
        subprocess.Popen(f'explorer "{os.path.abspath(recovered_dir)}"')
    except Exception as e:
        log_area.insert(tk.END, f"❌ Error: {e}\n")

# ---------------- GUI Setup ----------------
root = tk.Tk()
root.title("RecoverEase - File Recovery Tool")
root.geometry("650x450")

drive_var = tk.StringVar()
ttk.Label(root, text="Select Drive (for RAW mode):").pack(pady=5)
drive_dropdown = ttk.Combobox(root, textvariable=drive_var, values=["C","D","E","F"], state="readonly")
drive_dropdown.pack(pady=5)
drive_dropdown.current(1)  # Default to D:

ttk.Button(root, text="Start RAW Recovery", command=start_raw_recovery).pack(pady=10)
ttk.Button(root, text="Start Filesystem Recovery (pytsk3)", command=start_fs_recovery).pack(pady=10)

log_area = tk.Text(root, height=15, width=80, wrap="word")
log_area.pack(padx=10, pady=10)

root.mainloop()



