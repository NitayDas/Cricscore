from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.home, name = 'home'),
    
    path('matches/', MatchesList.as_view(), name='matches'),
    
    path('series/', SeriesList.as_view(), name='series'),
    
    path('seriesMatches/<int:seriesId>/', SeriesMatchesList.as_view(), name='seriesMatches'),
    
    path('matchDetails/<str:match_id>/', overSummary_and_Scoreboard.as_view(), name='matchDetails'),
    
    path('ballByball/<str:match_id>/', BallByBall.as_view(), name='ballByball'),
    
    path('register/',RegisterView.as_view(), name='register'),
    
    path('login/', LoginView.as_view(),name='login'),
    
    path('comments/<int:over_summary_id>/', CommentView.as_view()),
    
    path('comments/like/<int:comment_id>/',LikeCommentView.as_view(), name='like'),
    
    # path('finduser/', views.get_current_user, name = 'user'),
    path('top-comments/', GetTopComments.as_view(), name='top-comments'),
    
    path('recent-comments/', GetRecentComments.as_view(), name='recent-comments'),
    
    path('news/', GetNews.as_view(), name='news'),
]