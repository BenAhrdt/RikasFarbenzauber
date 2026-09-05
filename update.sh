#!/bin/sh
set -eu
if [ "$(id -u)" != 0 ]; then
    echo "Bitte als root oder mit sudo ./update.sh starten."
    exit 1
fi
RIKA_UPDATER=/usr/local/lib/rikas-updater
if [ ! -f "$RIKA_UPDATER/runner.py" ] || [ ! -f /etc/rikas-updater.json ]; then
    echo "Keine installierte LXC-Dienststruktur gefunden. Zuerst ./install.sh ausführen."
    exit 1
fi
case "${1:-}" in
    --worker)
        [ "$#" -eq 1 ] || exit 2
        exec /usr/bin/python3 "$RIKA_UPDATER/runner.py"
        ;;
    '')
        /usr/bin/python3 "$RIKA_UPDATER/request_update.py"
        # Also works when the path watcher has been disabled.
        systemctl start --no-block rikas-updater.service
        ;;
    *) echo "Verwendung: ./update.sh"; exit 2 ;;
esac
