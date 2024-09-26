from django.urls import path
from .consumers import CommentConsumer

websocket_urlpatterns = [
    path('ws/comments/<int:overSummaryId>/', CommentConsumer.as_asgi()),
]
