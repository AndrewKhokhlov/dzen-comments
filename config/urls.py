from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from comments.views import IndexView 

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    
    path('admin/', admin.site.urls),
    
    path('api/', include('comments.urls')),
    path('api/captcha/', include('rest_captcha.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)