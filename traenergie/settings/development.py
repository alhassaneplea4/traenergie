from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = ["127.0.0.1"]

# Dev: no collectstatic required
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
