from django.contrib import admin
from django.contrib.admin import StackedInline

from EventType.models import EventType, EventTypeDurations


class EventDurationStack(StackedInline):
    model = EventTypeDurations


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'visibility', 'event_calendar')
    search_fields = ('name',)

    inlines = [EventDurationStack]
