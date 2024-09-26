import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .serializers import CommentSerializer
from channels.db import database_sync_to_async
from .models import OverSummary, Comment


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.over_summary_id = self.scope['url_route']['kwargs']['over_summary_id']
        self.room_group_name = f'comments_{self.over_summary_id}'
        print(f"Attempting to connect to group: {self.room_group_name}")
        
        # Join the room group for this OverSummary
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        username = data['username']
        content = data['content']
        overSummaryId = data['overSummaryId']
        
        print(username)
        print(content)
        print(overSummaryId)
        
        

        # Save the comment to the database
        over_summary = await self.get_over_summary(overSummaryId)
        if over_summary:
            comment = await self.create_comment(over_summary, username, content)
            serializer = CommentSerializer(comment)

            # Broadcast the comment to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_comment',
                    'comment': serializer.data
                }
            )

    async def broadcast_comment(self, event):
        comment = event['comment']

        # Send the comment to the WebSocket
        await self.send(text_data=json.dumps({
            'comment': comment
        }))

    @database_sync_to_async
    def get_over_summary(self, over_summary_id):
       
        try:
            return OverSummary.objects.get(id=over_summary_id)
        except OverSummary.DoesNotExist:
            return None

    @database_sync_to_async
    def create_comment(self, over_summary, username, content):
        
        return Comment.objects.create(event=over_summary, username=username, content=content)
