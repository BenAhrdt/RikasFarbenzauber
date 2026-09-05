#!/bin/sh
set -eu
if [ "$(id -u)" != 0 ]; then
    echo "Bitte mit sudo ausführen: sudo ./scripts/update.sh"
    exit 1
fi
exec python3 /usr/local/lib/rikas-updater/request_update.py
