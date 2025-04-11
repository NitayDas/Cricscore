from django.urls import path
from .views import *

urlpatterns = [
    path('comment_percentage/', CommentMatchTypeReportView.as_view(), name='comment-percentage-report'),
    path('comment_sentiment_report/', CommentSentimentReportView.as_view(), name='comment-sentiment-report'),
]