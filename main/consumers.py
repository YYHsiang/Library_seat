import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
 
 
class ChatConsumer(WebsocketConsumer):
    # websocket建立连接时执行方法
    def connect(self):
        # 从url里获取聊天室名字，为每个房间建立一个频道组

        # 将当前频道加入频道组
        async_to_sync(self.channel_layer.group_add)(
            'chat',
            self.channel_name
        )
 
         # 接受所有websocket请求
        self.accept()
 
     # websocket断开时执行方法
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'chat',
            self.channel_name
        )
 
    # 从websocket接收到消息时执行函数
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 发送消息到频道组，频道组调用chat_message方法
        async_to_sync(self.channel_layer.group_send)(
            'chat',
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # 从频道组接收到消息后执行方法
    def chat_message(self, event):
        message = event['message']
        # 通过websocket发送消息到客户端
        self.send(text_data=json.dumps({
            'message': f'{message}'
        }))