from .base import *

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INTERNAL_IPS = ["127.0.0.1"]

# Dev: no collectstatic required
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
