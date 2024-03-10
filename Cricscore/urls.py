
from django.contrib import admin
from django.urls import path,include
from matches import views as match_view

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('', include('matches.urls')),
    # path('matches/', match_view.get_matches_list, name='matches'),
]
