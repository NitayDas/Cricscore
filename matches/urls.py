from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('matches/', views.get_matches_list, name='matches'),
    # path('upcomingmatches/', views.get_matches_list, name='upcoming_match'),
    # path('recentmatches/', views.get_matches_list, name='recent_match'),
]
