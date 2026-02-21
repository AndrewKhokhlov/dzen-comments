import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from comments.consumers import CommentConsumer

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    
    "websocket": URLRouter([
        path("ws/comments/", CommentConsumer.as_asgi()),
    ]),
})