from django.contrib import admin

from MultiEventType.models import MultiEventType, MultiEventConnection


@admin.register(MultiEventType)
class MultiEventTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(MultiEventConnection)
class MultiEventConnectionAdmin(admin.ModelAdmin):
    pass