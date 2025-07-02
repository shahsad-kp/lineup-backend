from django.contrib import admin
from django.contrib.admin import StackedInline

from EventType.models import EventType, EventTypeDurations, EventTypeLocations


class EventDurationStack(StackedInline):
    model = EventTypeDurations
    extra = 1


class EventLocationsStack(StackedInline):
    model = EventTypeLocations
    extra = 1


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'visibility', 'event_calendar')
    search_fields = ('name',)
    list_filter = ('visibility',)

    inlines = [EventDurationStack, EventLocationsStack]
