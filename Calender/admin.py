from django.contrib import admin

from Calender.models import Calendar, CalendarFetch, CalendarAccount, Availability, \
    UserCalendarSettings, ConflictCalendarGroup, ConflictCalendar


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "account", "last_updated")


@admin.register(CalendarAccount)
class CalendarAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "provider", "user")


@admin.register(CalendarFetch)
class CalendarFetchAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "started_on", "finished_on")


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("id", "timezone", "user", "created_at")


@admin.register(UserCalendarSettings)
class UserCalendarSettingsAdmin(admin.ModelAdmin):
    list_display = ("id", "user")


class ConflictCalendarInline(admin.TabularInline):
    model = ConflictCalendar


@admin.register(ConflictCalendarGroup)
class ConflictCalendarGroupAdmin(admin.ModelAdmin):
    inlines = (ConflictCalendarInline,)
