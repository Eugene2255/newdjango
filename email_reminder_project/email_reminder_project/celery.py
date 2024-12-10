from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_reminder_project.settings')

# Create a Celery app instance
app = Celery('email_reminder_project')

# Load config from Django's settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks()
