#!/usr/bin/env bash
# Restore Metrolinks (TKT) to the public front door. Does not delete St. Anthony.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

APP=/srv/stanthony
METRO=/srv/metrolinks

if [[ ! -d "$METRO" ]]; then
  echo "ERROR: $METRO missing — cannot rollback."
  exit 1
fi

echo "==> Rollback: public front door → Metrolinks (St. Anthony kept on disk)"

for site in stanthony stanthony-ip; do
  rm -f "/etc/nginx/sites-enabled/$site"
done

if [[ -f /etc/nginx/sites-available/metrolinks ]]; then
  ln -sf /etc/nginx/sites-available/metrolinks /etc/nginx/sites-enabled/metrolinks
fi
if [[ -f /etc/nginx/sites-available/metrolinks-ip ]]; then
  ln -sf /etc/nginx/sites-available/metrolinks-ip /etc/nginx/sites-enabled/metrolinks-ip
fi

if systemctl cat metrolinks-gunicorn.service &>/dev/null; then
  systemctl enable --now metrolinks-gunicorn || true
fi
for unit in metrolinks-celery metrolinks-celerybeat; do
  if systemctl cat "${unit}.service" &>/dev/null; then
    systemctl enable --now "$unit" || true
  fi
done

# Optionally leave stanthony running but not public; or stop it:
if systemctl cat stanthony-gunicorn.service &>/dev/null; then
  systemctl disable --now stanthony-gunicorn || true
fi

nginx -t
systemctl reload nginx

echo "==> Metrolinks is public again. St. Anthony remains at $APP"
