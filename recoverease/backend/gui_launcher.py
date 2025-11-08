import tkinter as tk
from tkinter import filedialog
from scanner.disk_scanner import list_logical_drives
from recovery.recovery_runner import run_recovery

def launch_gui():
    window = tk.Tk()
    window.title("RecoverEase - Forensic File Recovery")
    window.geometry("500x400")

    # Drive selection
    tk.Label(window, text="Select Drive to Scan:").pack()
    drive_var = tk.StringVar()
    drive_dropdown = tk.OptionMenu(window, drive_var, *list_logical_drives())
    drive_dropdown.pack()

    # Output folder
    tk.Label(window, text="Output Folder:").pack()
    output_var = tk.StringVar()
    tk.Entry(window, textvariable=output_var, width=40).pack()

    def browse_folder():
        folder = filedialog.askdirectory()
        if folder:
            output_var.set(folder)

    tk.Button(window, text="Browse", command=browse_folder).pack()

    # Flags
    preview_var = tk.BooleanVar()
    dryrun_var = tk.BooleanVar()
    force_var = tk.BooleanVar()
    usb_only_var = tk.BooleanVar()

    tk.Checkbutton(window, text="Preview Fragments", variable=preview_var).pack()
    tk.Checkbutton(window, text="Dry Run (No File Recovery)", variable=dryrun_var).pack()
    tk.Checkbutton(window, text="Force Recover Small Fragments", variable=force_var).pack()
    tk.Checkbutton(window, text="USB-Only Mode (Drive Recovery)", variable=usb_only_var).pack()

    # Log area
    log_area = tk.Text(window, height=10, width=60)
    log_area.pack()

    def on_run():
        drive = drive_var.get()
        output_folder = output_var.get() or "recovered"
        log_area.insert(tk.END, f"🔍 Scanning {drive}...\n")

        fragments = run_recovery(
            file_types=None,
            usb_only=usb_only_var.get(),
            preview=preview_var.get(),
            output_dir=output_folder,
            verbose=True,
            dryrun=dryrun_var.get(),
            drive=drive
        )

        log_area.insert(tk.END, f"✅ Recovered {len(fragments)} fragments\n")

    tk.Button(window, text="▶ Run Recovery", bg="green", fg="white", command=on_run).pack()

    window.mainloop()

if __name__ == "__main__":
    launch_gui()




