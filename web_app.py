import os
import datetime
import psutil
import subprocess
from flask import Flask, request, jsonify, send_from_directory, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from src.core.recoverer import Recoverer
from src.core.deleted_scanner import DeletedScanner
from src.utils.os_helpers import ensure_temp_dir, resolve_device_path, is_admin
from src.auth.db import init_db, register_user, verify_user

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.abspath(os.path.join(APP_ROOT, "..", "static"))
DATA_DIR = os.path.abspath(os.path.join(APP_ROOT, "..", "data"))
OUTPUT_DIR = os.path.abspath(os.path.join(APP_ROOT, "..", "temp_downloads"))
DELETED_DIR = os.path.abspath(os.path.join(APP_ROOT, "..", "temp_deleted"))
SIGNATURE_FILE = os.path.join(DATA_DIR, "file_signatures.json")

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=STATIC_DIR)
app.secret_key = "your-secret-key"
init_db()

recoverer = Recoverer(SIGNATURE_FILE)
ensure_temp_dir(OUTPUT_DIR)
ensure_temp_dir(DELETED_DIR)

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return app.send_static_file("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Missing credentials", 400
        if verify_user(username, password):
            session["user"] = username
            return redirect("/")
        return "Invalid credentials", 401
    return app.send_static_file("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Missing credentials", 400
        success = register_user(username, password)
        if success:
            return redirect("/login")
        return "Username already exists", 400
    return app.send_static_file("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/api/drives", methods=["GET"])
def list_drives():
    drives = []
    for part in psutil.disk_partitions():
        if part.device and part.fstype:
            drives.append(part.device.rstrip("\\"))
    if os.name == "nt":
        for i in range(10):
            path = f"\\\\.\\PhysicalDrive{i}"
            try:
                with open(path, "rb"):
                    drives.append(path)
            except Exception:
                continue
    return jsonify({"drives": drives})

@app.route("/api/scan", methods=["POST"])
def scan():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(force=True)
    raw_path = payload.get("image_path")
    extension = payload.get("extension", "jpg")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")

    try:
        image_path = resolve_device_path(raw_path)
    except Exception as e:
        return jsonify({"error": f"Invalid device path: {e}"}), 400

    if not image_path:
        return jsonify({"error": "Missing image_path"}), 400

    try:
        results = recoverer.scan_device(
            device_path=image_path,
            output_dir=OUTPUT_DIR,
            file_type=extension
        )

        def parse_date(d):
            try:
                return datetime.datetime.fromisoformat(d)
            except:
                return None

        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)

        filtered = []
        for r in results:
            mtime = r.get("mtime")
            if mtime:
                mtime_dt = datetime.datetime.fromtimestamp(mtime)
                if start_dt and mtime_dt < start_dt:
                    continue
                if end_dt and mtime_dt > end_dt:
                    continue
            r["filename"] = os.path.basename(r["path"])
            r["mtime"] = datetime.datetime.fromtimestamp(mtime).isoformat() if mtime else None
            filtered.append(r)

        return jsonify({"count": len(filtered), "results": filtered})

    except PermissionError:
        return jsonify({"error": "Permission denied. Run as admin/root for raw devices."}), 403
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Scan failed: {e}"}), 500

@app.route("/api/deleted_scan", methods=["POST"])
def scan_deleted():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(force=True)
    raw_path = payload.get("image_path")
    extensions = payload.get("extensions", [])
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    min_size = payload.get("min_size", 512)
    name_filter = payload.get("name_filter")

    try:
        image_path = resolve_device_path(raw_path)
    except Exception as e:
        return jsonify({"error": f"Invalid device path: {e}"}), 400

    try:
        scanner = DeletedScanner(image_path, DELETED_DIR)
        results = scanner.scan_deleted_files(
            extensions=extensions,
            start_date=start_date,
            end_date=end_date,
            min_size=min_size,
            name_filter=name_filter
        )

        formatted = [{
            "filename": os.path.basename(r["path"]),
            "type": r["type"],
            "size": r["size"],
            "mtime": r["mtime"]
        } for r in results]

        return jsonify({"count": len(formatted), "results": formatted})
    except Exception as e:
        print(f"[deleted scan] FS_Info failed: {e}")
        try:
            results = recoverer.scan_device(image_path, DELETED_DIR, file_type="mp3")
            formatted = [{
                "filename": os.path.basename(r["path"]),
                "type": r["type"],
                "size": r["size"],
                "mtime": r.get("mtime")
            } for r in results]
            return jsonify({"count": len(formatted), "results": formatted, "note": "Fallback to signature carving."})
        except Exception as e2:
            return jsonify({"error": f"Fallback carving failed: {e2}"}), 500

@app.route("/api/deep_carve", methods=["POST"])
def deep_carve():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(force=True)
    image_path = payload.get("image_path")
    tool = payload.get("tool", "photorec")
    output_dir = DELETED_DIR

    try:
        os.makedirs(output_dir, exist_ok=True)

        if tool == "photorec":
            cmd = ["photorec", "/d", output_dir, "/cmd", image_path, "options"]
        elif tool == "scalpel":
            cmd = ["scalpel", image_path, "-o", output_dir]
        else:
            return jsonify({"error": f"Unsupported tool: {tool}"}), 400

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({"error": f"{tool} failed: {result.stderr}"}), 500

        recovered_files = os.listdir(output_dir)
        formatted = [{
            "filename": f,
            "path": os.path.join(output_dir, f),
            "size": os.path.getsize(os.path.join(output_dir, f))
        } for f in recovered_files]

        return jsonify({"count": len(formatted), "results": formatted})
    except Exception as e:
        return jsonify({"error": f"Deep carve failed: {e}"}), 500

@app.route("/api/scan_carve", methods=["POST"])
def scan_carve():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(force=True)
    raw_path = payload.get("image_path")
    extension = (payload.get("extension") or "").strip().lower()

    if not raw_path:
        return jsonify({"error": "Missing image_path"}), 400

    try:
        try:
            target_path = resolve_device_path(raw_path)
        except ValueError:
            target_path = raw_path

        carve_exts = None
        if extension and extension.lower() != "all":
            carve_exts = [e.strip().lstrip(".").lower() for e in extension.split(",") if e.strip()]

        all_results = []
        if carve_exts:
            for ext in carve_exts:
                try:
                    partial = recoverer.scan_device(device_path=target_path, output_dir=OUTPUT_DIR, file_type=ext)
                    all_results.extend(partial)
                except Exception as e:
                    print(f"[carve] failed for ext {ext}: {e}")
        else:
            all_results = recoverer.scan_device(target_path, OUTPUT_DIR, None)

        out_results = []
        for r in all_results:
            try:
                p = r.get("path")
                fname = os.path.basename(p)
                recovered_at = datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat() if os.path.exists(p) else None
                out_results.append({
                    "path": p,
                    "filename": fname,
                    "type": r.get("type"),
                    "size": r.get("size"),
                    "offset": r.get("offset"),
                    "recovered_at": recovered_at
                })
            except Exception as e:
                print(f"[postprocess] {e}")
                continue

        return jsonify({
            "count": len(out_results),
            "results": out_results,
            "note": "Signature carving mode used (fallback)."
        })
    except Exception as e:
        return jsonify({"error": f"Carving failed: {e}"}), 500

@app.route("/downloads/<path:filename>", methods=["GET"])
def downloads(filename):
    if "user" not in session:
        return redirect("/login")

    for folder in [OUTPUT_DIR, DELETED_DIR]:
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            return send_from_directory(folder, filename, as_attachment=True)

    return "File not found", 404

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message")
    print(f"[chat] User message: {message}")
    return jsonify({"status": "received"})

if __name__ == "__main__":
    if not is_admin():
        print("Note: Accessing raw devices may require admin/root privileges.")
    app.run(host="127.0.0.1", port=5000, debug=True)
