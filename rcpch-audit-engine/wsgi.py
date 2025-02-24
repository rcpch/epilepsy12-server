"""
WSGI config for epilepsy12 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rcpch-audit-engine.settings')

application = get_wsgi_application()

application = WhiteNoise(application, index_file=True)
application.add_files("/app/staticdocs", prefix="docs/")