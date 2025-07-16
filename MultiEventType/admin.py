from django.contrib import admin

from MultiEventType.models import MultiEventType, MultiEventConnection

class MultiEventTypeConnectionInline(admin.TabularInline):
    model = MultiEventConnection
    extra = 1

@admin.register(MultiEventType)
class MultiEventTypeAdmin(admin.ModelAdmin):
    inlines = [MultiEventTypeConnectionInline]
