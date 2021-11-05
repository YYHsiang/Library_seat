import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
 
 
class ChatConsumer(WebsocketConsumer):
    # add websocket connect
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'chat',
            self.channel_name
        )
        self.accept()
 
     # disconnect the websocket
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'chat',
            self.channel_name
        )

    #send data to website
    def available_seat(self, event):
        available_seat = event['available_seat']
        seat_number = event['seat_number']
        occupy = event['occupy']
        print(occupy)
        self.send(text_data=json.dumps({
            'available_seat': f'{available_seat}',
            'seat_number' : f'{seat_number}',
            'occupy' : f'{occupy}'
        }))