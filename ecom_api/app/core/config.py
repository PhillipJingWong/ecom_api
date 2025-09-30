from pathlib import Path

CHUNKSIZE: int = 50_000
UPLOAD_DIR= Path(r"uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)