#!/usr/bin/env python3
"""Update /srv/stanthony/.env email settings. Reads EMAIL_PASS from the environment."""
import os
import sys
from pathlib import Path

ENV_PATH = Path(os.environ.get('STANTHONY_ENV', '/srv/stanthony/.env'))
password = os.environ.get('EMAIL_PASS', '').strip()
password_b64 = os.environ.get('EMAIL_PASS_B64', '').strip()
if password_b64:
    import base64
    password = base64.b64decode(password_b64).decode('utf-8')
if not password:
    sys.exit('EMAIL_PASS or EMAIL_PASS_B64 is required')
print('Password length:', len(password))

updates = {
    'EMAIL_HOST': 'mail.privateemail.com',
    'EMAIL_PORT': '587',
    'EMAIL_USE_TLS': 'True',
    'EMAIL_USE_SSL': 'False',
    'EMAIL_HOST_USER': 'info@stanthonyhcabossi.org',
    'EMAIL_HOST_PASSWORD': password,
    'DEFAULT_FROM_EMAIL': 'St. Anthony Health Centre <info@stanthonyhcabossi.org>',
    'CONTACT_NOTIFY_EMAIL': 'info@stanthonyhcabossi.org',
}

text = ENV_PATH.read_text() if ENV_PATH.exists() else ''
lines = []
seen = set()
for line in text.splitlines():
    if not line.strip() or line.lstrip().startswith('#') or '=' not in line:
        lines.append(line)
        continue
    key = line.split('=', 1)[0].strip()
    if key in updates:
        lines.append(f'{key}={updates[key]}')
        seen.add(key)
    else:
        lines.append(line)
for key, val in updates.items():
    if key not in seen:
        lines.append(f'{key}={val}')

ENV_PATH.write_text('\n'.join(lines) + '\n')
print('Updated email settings in', ENV_PATH, '(password redacted)')
