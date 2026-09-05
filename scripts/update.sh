#!/bin/sh
set -eu
RIKA_SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec "$RIKA_SOURCE/update.sh" "$@"
