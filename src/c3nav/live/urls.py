from django.urls import path

from c3nav.live.consumers import LiveConsumer, LiveUIConsumer

websocket_urlpatterns = [
    path('ws', LiveConsumer.as_asgi()),
    path('ui/ws', LiveUIConsumer.as_asgi()),
]
