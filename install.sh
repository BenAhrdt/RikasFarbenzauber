#!/bin/sh
set -eu
RIKA_SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ "$(id -u)" != 0 ]; then
    echo "Bitte als root oder mit sudo ./install.sh starten."
    exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
    apt-get update
    apt-get install -y python3
fi
exec python3 "$RIKA_SOURCE/deployment/install.py" --install-packages "$@"
