"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 1. Permitir peticiones http
django_asgi_app = get_asgi_application()

# 2. Permitir canales y websockets
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api_tareas.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # Si la petición empieza con http:// o https://
    "http": django_asgi_app,
    
    # Si la petición empieza con ws:// o wss://
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})