import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traenergie.settings.base")

from traenergie.wsgi import application

app = application
