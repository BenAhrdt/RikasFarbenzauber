"""Consistent online SQLite backup; destination must not already exist."""
import os
import sqlite3
import sys
from pathlib import Path
source = Path(os.environ.get('DATABASE_PATH', 'data/db.sqlite3')).resolve()
target = Path(sys.argv[1]).resolve()
if not source.is_file():
    raise SystemExit('Database does not exist')
# Exclusive creation prevents accidental backup overwrite.
fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
os.close(fd)
try:
    with sqlite3.connect(f'file:{source}?mode=ro', uri=True) as src, sqlite3.connect(target) as dest:
        src.backup(dest)
except Exception:
    target.unlink(missing_ok=True)
    raise
print(f'Backup created: {target}')
