from django.contrib import admin

from Calender.models import Calendar, CalendarFetch, CalendarAccount


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "account", "last_updated")


@admin.register(CalendarAccount)
class CalendarAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "provider", "user")


@admin.register(CalendarFetch)
class CalendarFetchAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "started_on", "finished_on")
