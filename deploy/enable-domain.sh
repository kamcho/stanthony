#!/usr/bin/env bash
# Apply stanthonyhcabossi.org nginx + .env on the VPS.
# Prerequisites: DNS A records for @ and www → 185.170.196.219 (not Namecheap parking).
# Usage: sudo bash /srv/stanthony/deploy/enable-domain.sh
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

APP=/srv/stanthony
DOMAIN=stanthonyhcabossi.org
WWW=www.stanthonyhcabossi.org
IP=185.170.196.219

if [[ ! -f "$APP/manage.py" ]]; then
  echo "ERROR: $APP missing"
  exit 1
fi

echo "==> Checking DNS (must point at $IP, not Namecheap parking)"
resolve() {
  python3 - <<'PY' "$1"
import socket, sys
host = sys.argv[1]
try:
    print(socket.gethostbyname(host))
except Exception as e:
    print("UNRESOLVED")
    sys.exit(0)
PY
}

APEX_IP="$(resolve "$DOMAIN" || true)"
WWW_IP="$(resolve "$WWW" || true)"
echo "    $DOMAIN → $APEX_IP"
echo "    $WWW → $WWW_IP"

if [[ "$APEX_IP" != "$IP" || "$WWW_IP" != "$IP" ]]; then
  echo ""
  echo "DNS is not ready yet. In Namecheap for $DOMAIN:"
  echo "  1. Turn OFF URL redirect / parking / Namecheap ParkingDNS"
  echo "  2. Use Advanced DNS with A records:"
  echo "       Host @   → $IP"
  echo "       Host www → $IP"
  echo "  3. Wait until: dig +short $DOMAIN   shows $IP"
  echo "Then re-run: sudo bash $APP/deploy/enable-domain.sh"
  exit 2
fi

echo "==> Installing nginx site"
cp "$APP/deploy/nginx/stanthony.conf" /etc/nginx/sites-available/stanthony
cp "$APP/deploy/nginx/stanthony-ip.conf" /etc/nginx/sites-available/stanthony-ip
ln -sf /etc/nginx/sites-available/stanthony /etc/nginx/sites-enabled/stanthony
ln -sf /etc/nginx/sites-available/stanthony-ip /etc/nginx/sites-enabled/stanthony-ip
nginx -t
systemctl reload nginx

echo "==> Updating .env hosts"
if [[ -f "$APP/.env" ]]; then
  python3 - <<'PY'
from pathlib import Path
env = Path('/srv/stanthony/.env')
text = env.read_text()
lines = []
replacements = {
    'ALLOWED_HOSTS': 'stanthonyhcabossi.org,www.stanthonyhcabossi.org,185.170.196.219,127.0.0.1,localhost',
    'CSRF_TRUSTED_ORIGINS': 'https://stanthonyhcabossi.org,https://www.stanthonyhcabossi.org,http://stanthonyhcabossi.org,http://www.stanthonyhcabossi.org',
    'SECURE_SSL_REDIRECT': 'True',
    'SESSION_COOKIE_SECURE': 'True',
    'CSRF_COOKIE_SECURE': 'True',
}
seen = set()
for line in text.splitlines():
    if not line.strip() or line.lstrip().startswith('#') or '=' not in line:
        lines.append(line)
        continue
    key, _, _ = line.partition('=')
    key = key.strip()
    if key in replacements:
        lines.append(f'{key}={replacements[key]}')
        seen.add(key)
    else:
        lines.append(line)
for key, val in replacements.items():
    if key not in seen:
        lines.append(f'{key}={val}')
env.write_text('\n'.join(lines) + '\n')
print('Updated', env)
PY
  chmod 640 "$APP/.env"
  chown stanthony:www-data "$APP/.env"
fi

systemctl restart stanthony-gunicorn

echo "==> Requesting Let's Encrypt certificate"
certbot --nginx -d "$DOMAIN" -d "$WWW" --non-interactive --agree-tos \
  --register-unsafely-without-email --redirect || {
  echo "WARN: certbot failed — site may still work on HTTP until retry"
}

systemctl reload nginx
echo "==> Done"
echo "    https://$WWW/"
echo "    https://$DOMAIN/"
