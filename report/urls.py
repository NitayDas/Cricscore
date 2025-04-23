from django.urls import path
from .views import *

urlpatterns = [
    path('MatchType_commentPercentage/', CommentMatchTypeReportView.as_view(), name='comment-percentage-by-match-type'),
    path('comment_sentiment_report/', CommentSentimentReportView.as_view(), name='comment-sentiment-report'),
    path('team_comment_stats/', TeamCommentStatsView.as_view(), name='team-comment-stats'),
    
]