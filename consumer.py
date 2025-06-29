import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from core.models import Song
from core.business_logic import handle_song_search, handle_url_search
from core.views import SearchSongs
from rest_framework.response import Response
from asgiref.sync import sync_to_async

# Custom ID for communication
SONG_REQUEST = "song_request"
URL_REQUEST = "url_request"
logger = logging.getLogger('comunication') 

class ChatConsumer(AsyncWebsocketConsumer):
   
    async def connect(self):
        logger.info("WebSocket connection established.")
        await self.accept()
       

    async def receive(self, text_data):
        # Parse the incoming message
        logger.debug(f"Received song request for")
        data = json.loads(text_data)
        if data.get('message') == SONG_REQUEST:
            song_name = data.get('song_name')

            input_data = {"data": song_name}
            result, status = await sync_to_async(handle_song_search)(input_data)

            await self.send(text_data=str(result))
        elif data.get('message') == URL_REQUEST:
            logger.debug(f"Received URL request for: {data}")
            input_data = {
                "url": data.get('url'),
                "id" : data.get('id', None)  # Optional ID field
            }
            result, status = await sync_to_async(handle_url_search)(input_data)

            await self.send(text_data=str(result))
    