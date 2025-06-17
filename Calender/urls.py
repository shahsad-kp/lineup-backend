from django.urls import path
from rest_framework.routers import DefaultRouter

from Calender.apis import CalendarAccountModelViewSet, CalendarModelViewSet, CalendarSettingsView, \
    ConflictCalendarModelViewSet, AvailabilityModelViewSet

router = DefaultRouter()
router.register('accounts', CalendarAccountModelViewSet, basename='accounts')
router.register('calendar', CalendarModelViewSet, basename='calendar')
router.register('conflict-calendar', ConflictCalendarModelViewSet, basename='conflict-calendar')
router.register('availability', AvailabilityModelViewSet, basename='availability')

urlpatterns = [
                  path('calendar-settings/', CalendarSettingsView.as_view()),
              ] + router.urls
