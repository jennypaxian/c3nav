from django.urls import path

from c3nav.live.consumers import LiveConsumer, LiveUIConsumer

websocket_urlpatterns = [
    path('ws', MeshConsumer.as_asgi()),
    path('ui/ws', MeshUIConsumer.as_asgi()),
]
