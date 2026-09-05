#!/bin/sh
set -eu
# Keep entry points executable even when upgrading with the older ZIP extractor.
chmod +x install.sh update.sh
.venv/bin/python scripts/sync_assets.py
.venv/bin/python manage.py check
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python -m compileall -q config studio
