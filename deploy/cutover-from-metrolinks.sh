#!/usr/bin/env bash
# Point the public VPS front door at St. Anthony instead of Metrolinks (TKT).
#
# SAFETY:
#   - Does NOT delete /srv/metrolinks (TKT stays on disk)
#   - Does NOT drop the metrolinks Postgres DB
#   - Does NOT edit Soma Smart (elearning) nginx
#   - Stops Metrolinks systemd units so they don't consume RAM (can re-enable later)
#   - Disables Metrolinks nginx sites and enables St. Anthony sites
#
# Usage: sudo bash /srv/stanthony/deploy/cutover-from-metrolinks.sh
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

APP=/srv/stanthony
METRO=/srv/metrolinks
ELEARNING_NGINX=/etc/nginx/sites-available/elearning
ELEARNING_BEFORE=""
if [[ -f "$ELEARNING_NGINX" ]]; then
  ELEARNING_BEFORE="$(sha256sum "$ELEARNING_NGINX")"
fi

if [[ ! -f "$APP/manage.py" ]]; then
  echo "ERROR: Install St. Anthony first: sudo bash $APP/deploy/install-beside-somasmart.sh"
  exit 1
fi

if ! systemctl is-active --quiet stanthony-gunicorn; then
  echo "ERROR: stanthony-gunicorn is not active. Run install-beside-somasmart.sh first."
  exit 1
fi

echo "==> Cutover: Metrolinks public → St. Anthony (TKT files kept)"

# Stop Metrolinks app processes (leave files + DB)
for unit in metrolinks-gunicorn metrolinks-celery metrolinks-celerybeat; do
  if systemctl cat "${unit}.service" &>/dev/null; then
    systemctl disable --now "$unit" || true
    echo "    Stopped/disabled $unit"
  fi
done

# Disable Metrolinks nginx sites (do not delete the site files under sites-available)
for site in metrolinks metrolinks-ip; do
  if [[ -L "/etc/nginx/sites-enabled/$site" || -f "/etc/nginx/sites-enabled/$site" ]]; then
    rm -f "/etc/nginx/sites-enabled/$site"
    echo "    Disabled nginx site: $site"
  fi
done

# Keep a copy of previous Metrolinks nginx configs if present (reference only)
mkdir -p "$APP/deploy/backup-metrolinks-nginx"
for site in metrolinks metrolinks-ip; do
  if [[ -f "/etc/nginx/sites-available/$site" ]]; then
    cp -a "/etc/nginx/sites-available/$site" "$APP/deploy/backup-metrolinks-nginx/"
  fi
done

# Install St. Anthony nginx
cp "$APP/deploy/nginx/stanthony.conf" /etc/nginx/sites-available/stanthony
cp "$APP/deploy/nginx/stanthony-ip.conf" /etc/nginx/sites-available/stanthony-ip
ln -sf /etc/nginx/sites-available/stanthony /etc/nginx/sites-enabled/stanthony
ln -sf /etc/nginx/sites-available/stanthony-ip /etc/nginx/sites-enabled/stanthony-ip

ufw allow 8080/tcp || true
nginx -t
systemctl reload nginx

if [[ -n "$ELEARNING_BEFORE" ]]; then
  ELEARNING_AFTER="$(sha256sum "$ELEARNING_NGINX")"
  if [[ "$ELEARNING_BEFORE" != "$ELEARNING_AFTER" ]]; then
    echo "ERROR: elearning nginx changed during cutover — investigate."
    exit 1
  fi
  echo "==> Verified: elearning nginx unchanged"
fi

if [[ -d "$METRO" ]]; then
  echo "==> TKT preserved at $METRO"
  du -sh "$METRO" 2>/dev/null || true
else
  echo "NOTE: $METRO not found on this VPS (nothing to preserve)"
fi

echo ""
echo "==> Cutover complete"
echo "    Public IP:  http://185.170.196.219/"
echo "    Alt port:   http://185.170.196.219:8080/"
echo "    App:        $APP"
echo ""
echo "Rollback (restore Metrolinks public, keep St. Anthony on disk):"
echo "  sudo bash $APP/deploy/rollback-to-metrolinks.sh"
