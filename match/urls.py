from django.urls import path
from . import views
from .views import MatchesList

urlpatterns = [
    path('', views.home, name = 'home'),
    path('matches/', MatchesList.as_view(), name='matches'),
]