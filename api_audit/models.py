import uuid

from django.db.models import TextField, IntegerField, DateTimeField, JSONField, CharField, ForeignKey, \
    Model, SET_NULL, GenericIPAddressField, UUIDField, Index, DurationField

from User.models import User
from api_audit.choices import StatusCode, HTTPMethod


class APIRequestLog(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL, db_index=True)
    method = CharField(max_length=10, db_index=True, choices=HTTPMethod)
    path = TextField()
    status_code = IntegerField(db_index=True, choices=StatusCode)
    duration = DurationField()
    timestamp = DateTimeField(auto_now_add=True, db_index=True)
    query_params = JSONField(null=True, blank=True)
    request_data = JSONField(null=True, blank=True)
    remote_ip = GenericIPAddressField(null=True, blank=True, db_index=True)
    error_trace = TextField(null=True, blank=True)

    class Meta:
        db_table = "api_request_log"
        indexes = [
            Index(fields=['timestamp']),
            Index(fields=['status_code']),
            Index(fields=['method']),
            Index(fields=['remote_ip']),
            Index(fields=['user']),
        ]
        ordering = ['-timestamp']
        verbose_name = 'API Request Log'
        verbose_name_plural = 'API Request Logs'

    def __str__(self):
        user = self.user.email if self.user else None
        return f"[{self.timestamp}] {self.method} {self.path} ({self.status_code}) {f' by {user}' if user else ''}"

    def __repr__(self):
        return f"<APIRequestLog {self.id} - {self.method} {self.path} ({self.status_code}) by {self.user}>"
