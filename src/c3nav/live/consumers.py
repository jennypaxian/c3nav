import asyncio
import traceback
from asyncio import get_event_loop
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum, auto, unique
from functools import cached_property
from typing import Optional

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from c3nav.routing.locator import Locator

class LiveConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()

    async def connect(self):
        pass

    async def disconnect(self, close_code):
        pass

    async def send_msg(self, msg: MeshMessage, sender=None, exclude_uplink_address=None):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        pass

class LiveUIConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self):
        super().__init__()

    async def connect(self):
        pass

    async def receive_json(self, content, **kwargs):
        pass

    async def disconnect(self, code):
        pass