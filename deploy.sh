#!/bin/bash
# Redeploy St. Anthony on the shared VPS (after git pull / rsync).
# Does not touch Soma Smart or delete TKT/Metrolinks.
# Usage: bash deploy.sh
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

VENV_DIR="${VENV_DIR:-$APP_DIR/.venv}"
PYTHON="${PYTHON:-$VENV_DIR/bin/python}"
PIP="${PIP:-$VENV_DIR/bin/pip}"
APP_USER="${APP_USER:-stanthony}"

echo "==> Deploying St. Anthony in $APP_DIR"

if [ ! -x "$PYTHON" ]; then
  echo "ERROR: Python not found at $PYTHON"
  echo "First-time install: sudo bash deploy/install-beside-somasmart.sh"
  exit 1
fi

if [ ! -f "$APP_DIR/.env" ]; then
  echo "ERROR: Missing $APP_DIR/.env — copy .env.hostinger.example or run install script"
  exit 1
fi

echo "==> Installing dependencies"
"$PIP" install -r requirements.txt --quiet

run_manage() {
  if id "$APP_USER" >/dev/null 2>&1 && [ "$(id -u)" -eq 0 ]; then
    sudo -u "$APP_USER" "$PYTHON" manage.py "$@"
  else
    "$PYTHON" manage.py "$@"
  fi
}

echo "==> Running migrations"
run_manage migrate --noinput

echo "==> Collecting static files"
run_manage collectstatic --noinput

if [ -d "$APP_DIR/staticfiles" ]; then
  find "$APP_DIR/staticfiles" -type d -exec chmod 755 {} +
  find "$APP_DIR/staticfiles" -type f -exec chmod 644 {} +
fi

mkdir -p "$APP_DIR/media"

if systemctl cat stanthony-gunicorn.service &>/dev/null; then
  echo "==> Restarting stanthony-gunicorn"
  sudo systemctl restart stanthony-gunicorn
else
  echo "==> Skipping stanthony-gunicorn (not installed)"
fi

if systemctl cat elearning.service &>/dev/null; then
  if systemctl is-active --quiet elearning; then
    echo "==> Soma Smart (elearning) still active"
  else
    echo "WARN: elearning service is not active — check: systemctl status elearning"
  fi
fi

if [ -d /srv/metrolinks ]; then
  echo "==> TKT/Metrolinks still present at /srv/metrolinks (not deleted)"
fi

echo "==> Deploy finished OK"
echo "    Logs: sudo journalctl -u stanthony-gunicorn -f"
