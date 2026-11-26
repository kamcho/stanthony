# Deploy St. Anthony in place of TKT (Metrolinks) — keep TKT on disk

Shared Hostinger VPS already runs:

| App | Path | Notes |
|-----|------|--------|
| Soma Smart | `/srv/elearning` | Untouched |
| Metrolinks / TKT (ISP billing) | `/srv/metrolinks` | **Kept** — stopped from public only |
| St. Anthony | `/srv/stanthony` | New public site |

TKT locally lives under `Downloads/TKT`. On the VPS it is Metrolinks at `/srv/metrolinks`.

---

## What cutover does / does not do

**Does**
- Install St. Anthony at `/srv/stanthony` with its own Postgres DB + gunicorn
- Point nginx (IP + previous Metrolinks hostnames) at St. Anthony
- Stop Metrolinks systemd units so they free RAM

**Does not**
- Delete `/srv/metrolinks` or the local `TKT` folder
- Drop the `metrolinks` Postgres database
- Change Soma Smart / elearning nginx

---

## Upload + install

From your PC (PowerShell), sync the project:

```powershell
rsync -avz --exclude .venv --exclude __pycache__ --exclude db.sqlite3 `
  "C:\Users\USER\Downloads\stanthony/" root@185.170.196.219:/srv/stanthony/
```

On the VPS:

```bash
ssh root@185.170.196.219

# 1) Install beside Soma Smart (creates DB/user/venv/service)
sudo bash /srv/stanthony/deploy/install-beside-somasmart.sh

# 2) Take public front door from Metrolinks (TKT files stay)
sudo bash /srv/stanthony/deploy/cutover-from-metrolinks.sh

# 3) Staff login
sudo -u stanthony /srv/stanthony/.venv/bin/python /srv/stanthony/manage.py createsuperuser
```

Open: `http://185.170.196.219/`

---

## Updates later

```bash
cd /srv/stanthony
# pull or rsync again
bash deploy.sh
```

---

## Rollback to TKT public

```bash
sudo bash /srv/stanthony/deploy/rollback-to-metrolinks.sh
```

St. Anthony remains at `/srv/stanthony`; Metrolinks serves the IP/domains again.

---

## Smoke checks

```bash
systemctl is-active elearning stanthony-gunicorn
ls -la /srv/metrolinks          # should still exist
curl -I http://185.170.196.219/
curl -I https://somasmartassesments.com/
sudo journalctl -u stanthony-gunicorn -n 40 --no-pager
```
