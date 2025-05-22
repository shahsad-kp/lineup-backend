from django.urls import path

from Calender.apis import ConnectAccountView, GetCalendarAccounts

urlpatterns = [
    path('connect/', ConnectAccountView.as_view(), name='connect'),
    path('list-accounts/', GetCalendarAccounts.as_view(), name='list-accounts'),
]
