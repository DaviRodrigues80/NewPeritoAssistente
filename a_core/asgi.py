"""
ASGI config for a_core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from whitenoise import WhiteNoise
from a_core.settings import BASE_DIR

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_core.settings')

application = get_asgi_application()
application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles'))