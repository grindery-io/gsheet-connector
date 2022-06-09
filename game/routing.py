from django.conf.urls import url

from game.consumers import SocketAdapter

websocket_urlpatterns = [
    url(r'^ws/', SocketAdapter.as_asgi()),
]