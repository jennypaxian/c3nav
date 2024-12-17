import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveMessageConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()

    async def connect(self):
        self.accept();

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.send(text_data=json.dumps({
            'message': message
        }))
