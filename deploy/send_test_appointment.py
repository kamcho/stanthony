#!/usr/bin/env python3
import os
import sys

os.chdir(os.environ.get('STANTHONY_APP', '/srv/stanthony'))
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from django.conf import settings
from django.core.mail import EmailMessage, get_connection

body = (
    "New appointment request from the website\n"
    "========================================\n\n"
    "Name:    Test Visitor\n"
    "Phone:   0700000000\n"
    "Email:   visitor@example.com\n"
    "Service: Out-patient\n\n"
    "Notes:\nSimulated form submission from diagnostics.\n"
)
print('FROM', settings.DEFAULT_FROM_EMAIL)
print('TO', settings.CONTACT_NOTIFY_EMAIL)
print('PASS len', len(settings.EMAIL_HOST_PASSWORD or ''))
conn = get_connection(timeout=30)
conn.open()
n = EmailMessage(
    subject='Appointment request — Test Visitor (Out-patient)',
    body=body,
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=[settings.CONTACT_NOTIFY_EMAIL],
    reply_to=['visitor@example.com'],
    connection=conn,
).send(fail_silently=False)
conn.close()
print('SIMULATED FORM EMAIL SENT', n)
