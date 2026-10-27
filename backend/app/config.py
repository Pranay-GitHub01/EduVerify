from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / 'data'
UPLOAD_DIR = DATA_DIR / 'uploads'
DB_PATH = DATA_DIR / 'eduverify.sqlite3'
MAX_UPLOAD_MB = int(os.getenv('MAX_UPLOAD_MB', '12'))
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.txt'}
