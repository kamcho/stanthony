#!/usr/bin/env python3
"""Test Django SMTP settings. Exit 0 on success."""
import os
import sys
import traceback

os.chdir(os.environ.get('STANTHONY_APP', '/srv/stanthony'))
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from django.conf import settings
from django.core.mail import EmailMessage, get_connection

print('HOST', settings.EMAIL_HOST)
print('PORT', settings.EMAIL_PORT)
print('TLS', settings.EMAIL_USE_TLS, 'SSL', settings.EMAIL_USE_SSL)
print('USER', settings.EMAIL_HOST_USER)
print('PASS len', len(settings.EMAIL_HOST_PASSWORD or ''))
print('FROM', settings.DEFAULT_FROM_EMAIL)
print('TO', settings.CONTACT_NOTIFY_EMAIL)

try:
    conn = get_connection(timeout=30)
    conn.open()
    print('SMTP open: OK')
    sent = EmailMessage(
        subject='St Anthony SMTP OK',
        body='SMTP authentication works from the VPS.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_NOTIFY_EMAIL],
        connection=conn,
    ).send(fail_silently=False)
    conn.close()
    print('SMTP SEND OK', sent)
except Exception as exc:
    print('SMTP FAILED:', type(exc).__name__, exc)
    traceback.print_exc()
    sys.exit(1)
