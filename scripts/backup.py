"""Create a consistent SQLite backup, including committed WAL data."""
import argparse
import sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('destination');a=p.parse_args()
source=Path(a.source).resolve();destination=Path(a.destination).resolve()
if not source.is_file():p.error('source does not exist')
if destination.exists():p.error('destination must not already exist')
with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src:
    with sqlite3.connect(destination) as dst:
        src.backup(dst)
        if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise SystemExit('Backup integrity check failed')
print('Consistent backup created:',destination)
