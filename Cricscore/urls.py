from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from match import views as match_view

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('', include('match.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
