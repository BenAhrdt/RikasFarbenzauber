#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
RIKA_LAN_IP="${1:-192.168.2.131}"
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,$RIKA_LAN_IP"
exec .venv/bin/python manage.py runserver "$RIKA_LAN_IP:8000" --noreload
