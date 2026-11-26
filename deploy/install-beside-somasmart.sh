#!/usr/bin/env bash
# Install St. Anthony NEXT TO Soma Smart on the shared VPS.
# Safe: does not edit /srv/elearning and does NOT delete /srv/metrolinks (TKT).
#
# Prerequisites: code already at /srv/stanthony
# Usage: sudo bash /srv/stanthony/deploy/install-beside-somasmart.sh
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

APP=/srv/stanthony
ELEARNING_NGINX=/etc/nginx/sites-available/elearning
ELEARNING_BEFORE=""
if [[ -f "$ELEARNING_NGINX" ]]; then
  ELEARNING_BEFORE="$(sha256sum "$ELEARNING_NGINX")"
fi

if [[ ! -f "$APP/manage.py" ]]; then
  echo "ERROR: $APP/manage.py missing. Upload/clone the app first:"
  echo "  rsync -avz ./stanthony/ root@VPS:/srv/stanthony/"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx \
  certbot python3-certbot-nginx git curl ufw \
  libpq-dev postgresql postgresql-contrib || true
systemctl enable --now postgresql nginx || true

if ! id stanthony >/dev/null 2>&1; then
  useradd --system --gid www-data --home-dir "$APP" --shell /usr/sbin/nologin stanthony
fi

python3 -m venv "$APP/.venv"
"$APP/.venv/bin/pip" install --upgrade pip
"$APP/.venv/bin/pip" install --no-cache-dir -r "$APP/requirements.txt"

DB_PASSWORD=""
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='stanthony'" | grep -q 1; then
  DB_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
  sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE USER stanthony WITH PASSWORD '${DB_PASSWORD}'"
fi
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='stanthony'" | grep -q 1; then
  sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE stanthony OWNER stanthony"
fi
sudo -u postgres psql -v ON_ERROR_STOP=1 -d stanthony -c "GRANT ALL ON SCHEMA public TO stanthony"

if [[ ! -f "$APP/.env" ]]; then
  if [[ -z "${DB_PASSWORD}" ]]; then
    DB_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
    sudo -u postgres psql -v ON_ERROR_STOP=1 -c "ALTER USER stanthony WITH PASSWORD '${DB_PASSWORD}'"
  fi
  SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
  umask 077
  cat > "$APP/.env" << EOF
DEBUG=False
SECRET_KEY=${SECRET_KEY}
TIME_ZONE=Africa/Nairobi
LOG_LEVEL=INFO

ALLOWED_HOSTS=185.170.196.219,127.0.0.1,localhost,metrolinkssolutionltd.co.ke,www.metrolinkssolutionltd.co.ke,tickets.metrolinkssolutionltd.co.ke
CSRF_TRUSTED_ORIGINS=http://185.170.196.219,http://metrolinkssolutionltd.co.ke,http://www.metrolinkssolutionltd.co.ke,http://tickets.metrolinkssolutionltd.co.ke

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

DB_ENGINE=postgres
DB_NAME=stanthony
DB_USER=stanthony
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=127.0.0.1
DB_PORT=5432

GUNICORN_WORKERS=2
GUNICORN_BIND=unix:/run/stanthony/stanthony.sock
EOF
  echo "==> Created $APP/.env"
fi

mkdir -p "$APP/media" "$APP/staticfiles"
chown -R stanthony:www-data "$APP"
chmod 640 "$APP/.env"
chmod 755 /srv "$APP"

sudo -u stanthony "$APP/.venv/bin/python" "$APP/manage.py" migrate --noinput
sudo -u stanthony "$APP/.venv/bin/python" "$APP/manage.py" collectstatic --noinput
find "$APP/staticfiles" -type d -exec chmod 755 {} +
find "$APP/staticfiles" -type f -exec chmod 644 {} +

cp "$APP/deploy/systemd/stanthony-gunicorn.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now stanthony-gunicorn
systemctl is-active --quiet stanthony-gunicorn

if [[ -n "$ELEARNING_BEFORE" ]]; then
  ELEARNING_AFTER="$(sha256sum "$ELEARNING_NGINX")"
  if [[ "$ELEARNING_BEFORE" != "$ELEARNING_AFTER" ]]; then
    echo "ERROR: elearning nginx site changed — aborting."
    exit 1
  fi
  echo "==> Verified: elearning nginx site unchanged"
fi

if [[ -d /srv/metrolinks ]]; then
  echo "==> TKT/Metrolinks still present at /srv/metrolinks (untouched)"
fi

echo ""
echo "==> St. Anthony installed beside Soma Smart"
echo "    App:     $APP"
echo "    Service: stanthony-gunicorn"
echo "    DB:      postgres / stanthony"
echo ""
echo "Next: take the public front door from Metrolinks (TKT kept on disk):"
echo "  sudo bash $APP/deploy/cutover-from-metrolinks.sh"
echo "  sudo -u stanthony $APP/.venv/bin/python $APP/manage.py createsuperuser"
