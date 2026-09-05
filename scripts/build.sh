#!/bin/sh
set -eu
.venv/bin/python scripts/sync_assets.py
.venv/bin/python manage.py check
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python -m compileall -q config studio
