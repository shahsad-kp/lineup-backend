from django.contrib.admin import EmptyFieldListFilter, SimpleListFilter, register, ModelAdmin

from api_audit.models import APIRequestLog


class UsedStatusCodeFilter(SimpleListFilter):
    title = 'status code'
    parameter_name = 'status_code'

    def lookups(self, request, model_admin):
        used_codes = list(set(APIRequestLog.objects.values_list('status_code', flat=True)))
        return [
            (code, dict(APIRequestLog._meta.get_field('status_code').choices).get(code, str(code)))
            for code in sorted(used_codes)
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status_code=self.value())
        return queryset

@register(APIRequestLog)
class APIRequestLogAdmin(ModelAdmin):
    list_filter = [
        'method',
        UsedStatusCodeFilter,
        ('error_trace', EmptyFieldListFilter),

    ]