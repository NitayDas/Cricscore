from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('', views.home, name = 'home'),
    path('matches/', MatchesList.as_view(), name='matches'),
    # path('matchDetails/<str:match_id>/',MatchDetails.as_view(),name='matchDetails'),
    # path('scoreboard/<str:match_id>/',ScoreboardDetails.as_view(),name='scoreboard'),
    path('matchDetails/<str:match_id>/', overSummary_and_Scoreboard.as_view(), name='matchDetails'),
    path('register/',RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(),name='login'),
    path('comments/<int:over_summary_id>/', CommentView.as_view()),
]