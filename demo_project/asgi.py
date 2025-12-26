"""
ASGI config for demo_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo_project.settings')
django.setup()

from task.middleware import JWTAuthMiddleware
from task.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket" : JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    )
})
