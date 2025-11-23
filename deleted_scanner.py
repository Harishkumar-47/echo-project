import pytsk3
import os
import datetime

class DeletedScanner:
    def __init__(self, image_path, output_dir):
        self.image_path = image_path
        self.output_dir = output_dir

        img = pytsk3.Img_Info(image_path)

        # Detect partition offset
        try:
            volume = pytsk3.Volume_Info(img)
            offset = None
            for part in volume:
                desc = part.desc.decode("utf-8", errors="ignore").lower()
                if "ntfs" in desc or "fat" in desc or "linux" in desc:
                    offset = part.start * 512
                    print(f"[debug] Using partition offset: {offset}")
                    break
            if offset is None:
                raise Exception("No valid partition found")
        except Exception as e:
            print(f"[warn] Partition scan failed or not needed: {e}")
            offset = 0  # fallback for flat image or logical volume

        self.fs = pytsk3.FS_Info(img, offset=offset)

    def scan_deleted_files(self, extensions=None, start_date=None, end_date=None, min_size=512, name_filter=None):
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        results = []
        self._scan_dir(self.fs.open_dir(path="/"), extensions, results, start_dt, end_dt, min_size, name_filter)
        return results

    def _parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.datetime.fromisoformat(date_str)
        except Exception:
            return None

    def _scan_dir(self, directory, extensions, results, start_dt, end_dt, min_size, name_filter, path="/"):
        for entry in directory:
            if not entry.info.name or entry.info.name.name in [b".", b".."]:
                continue

            name = entry.info.name.name.decode("utf-8", errors="ignore")
            meta = entry.info.meta
            full_path = os.path.join(path, name)

            if not meta or not (meta.flags & pytsk3.TSK_FS_META_FLAG_UNALLOC):
                continue

            ext = os.path.splitext(name)[1].lower().strip(".")
            if extensions and ext not in extensions:
                continue
            if name_filter and name_filter.lower() not in name.lower():
                continue
            if meta.size < min_size:
                continue

            mtime = meta.mtime
            if mtime:
                mtime_dt = datetime.datetime.fromtimestamp(mtime)
                if start_dt and mtime_dt < start_dt:
                    continue
                if end_dt and mtime_dt > end_dt:
                    continue
            else:
                if start_dt or end_dt:
                    continue

            try:
                file_obj = self.fs.open_meta(inode=meta.addr)
                data = file_obj.read_random(0, meta.size)
                out_name = f"deleted_{meta.addr}_{name}"
                out_path = os.path.join(self.output_dir, out_name)

                os.makedirs(self.output_dir, exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(data)

                results.append({
                    "filename": out_name,
                    "type": ext,
                    "size": meta.size,
                    "mtime": mtime_dt.isoformat() if mtime else None,
                    "path": out_path
                })
            except Exception as e:
                print(f"[error] Failed to recover {name}: {e}")

            if meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                try:
                    subdir = entry.as_directory()
                    self._scan_dir(subdir, extensions, results, start_dt, end_dt, min_size, name_filter, full_path)
                except Exception:
                    continue
