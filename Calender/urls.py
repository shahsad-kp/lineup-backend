from django.urls import path

from Calender.apis import ConnectAccountView

urlpatterns = [
    path('connect/', ConnectAccountView.as_view(), name='connect'),
]