from scanner.disk_scanner import read_raw_sectors

data = read_raw_sectors("D", verbose=True)
print(f"✅ Successfully read {len(data)} bytes from D:")
