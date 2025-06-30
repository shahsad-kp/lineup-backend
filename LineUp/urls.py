from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Authentication.urls')),
    path('', include('Calender.urls')),
    path('', include('EventType.urls')),
    path('', include('MultiEventType.urls')),
]
