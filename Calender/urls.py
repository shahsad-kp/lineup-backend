from django.urls import path
from rest_framework.routers import DefaultRouter

from Calender.apis import CalendarAccountModelViewSet, CalendarModelViewSet, CalendarSettingsView

router = DefaultRouter()
router.register('accounts', CalendarAccountModelViewSet, basename='accounts')
router.register('calendar', CalendarModelViewSet, basename='calendar')

urlpatterns = [
                  path('calendar-settings/', CalendarSettingsView.as_view()),
              ] + router.urls
