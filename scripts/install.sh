#!/bin/sh
set -eu
RIKA_SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$RIKA_SOURCE/deployment/install.py" "$@"
