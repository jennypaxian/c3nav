from django.urls import path

from c3nav.live.consumers import LiveMessageConsumer

websocket_urlpatterns = [
    path('/ws/messages', LiveMessageConsumer.as_asgi())
]
