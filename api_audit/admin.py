from django.contrib import admin

from api_audit.models import APIRequestLog


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_filter = [
        'method',
        'status_code',
        'user'
    ]