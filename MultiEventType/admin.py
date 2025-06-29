from django.contrib import admin

from MultiEventType.models import MultiEventType


@admin.register(MultiEventType)
class MultiEventTypeAdmin(admin.ModelAdmin):
    pass