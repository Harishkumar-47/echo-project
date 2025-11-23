from scanner.disk_scanner import recover_files

if __name__ == "__main__":
    DRIVE = "D"
    OUTPUT = "recovered"
    SECTOR_SIZE = 512
    CHUNK_SECTORS = 100          # 50 KB per chunk
    MAX_BYTES = 20 * 1024 * 1024 # Limit to 20 MB for testing
    FILE_TYPES = ["jpg", "png", "pdf", "mp4", "zip"]
    FRAGMENT_SIZE = 1024 * 500   # 500 KB per carved file

    recover_files(
        drive_letter=DRIVE,
        output_dir=OUTPUT,
        sector_size=SECTOR_SIZE,
        chunk_sectors=CHUNK_SECTORS,
        max_bytes=MAX_BYTES,
        file_types=FILE_TYPES,
        fragment_size=FRAGMENT_SIZE,
        verbose=True
    )
