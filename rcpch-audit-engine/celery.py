import logging
import os

from celery import Celery
from django.conf import settings

# Logging setup
logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rcpch-audit-engine.settings")

app = Celery("rcpch-audit-engine")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.debug("Request: {0!r}".format(self.request))