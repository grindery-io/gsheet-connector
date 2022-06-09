from django.conf.urls import url

from game.adapter import SocketAdapter

websocket_urlpatterns = [
    url(r'^ws/play/(?P<room_code>\w+)/$', SocketAdapter.as_asgi()),
]