# RecoverEase – Forensic File Recovery Tool

RecoverEase is a Python-based forensic recovery tool designed to scan raw disk sectors and reconstruct deleted files using signature-based detection. It supports recovery of formats like JPG, PNG, PDF, XLSX, MP3, and MP4, and includes a GUI for easy use.

---

## 🔧 Features

- Raw sector scanning via low-level disk access
- Signature-based fragment detection
- Entropy and size filtering
- GUI launcher with Tkinter
- Toast notifications via `plyer`
- Fallback recovery if no matches found
- USB-only mode for safe scanning

---

## 🖥️ GUI Options

- 📁 Output Folder selection
- 🔍 Preview Fragments
- 🚫 Dry Run (no file save)
- 📄 Force Recover Small Fragments
- 🖴 USB-Only Mode

![RecoverEase GUI showing scan options and recovery controls](screenshot.png)

---

## ▶️ How to Run

1. Right-click `launch_recoverease.bat` → “Run as administrator”
2. Select a USB drive with deleted files
3. Click “Run Recovery”
4. Recovered files will appear in `recovered/`

---

## 📂 Folder Structure

