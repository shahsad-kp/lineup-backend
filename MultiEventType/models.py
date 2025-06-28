from uuid import uuid4

from django.db.models import Model, UUIDField, DateTimeField, CharField, TextField, ForeignKey, CASCADE

from MultiEventType.choices import MultiEventVisibility
from User.models import User


class MultiEventType(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    name = CharField(max_length=255)
    description = TextField(blank=True, default='')
    owner = ForeignKey(User, on_delete=CASCADE)
    visibility = CharField(max_length=100, choices=MultiEventVisibility, default=MultiEventVisibility.PUBLIC)

    class Meta:
        db_table = 'multi_event_type'
        verbose_name = 'Multi Event Type'
        verbose_name_plural = 'Multi Event Types'
        ordering = ['-created_at']