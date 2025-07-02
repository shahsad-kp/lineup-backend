from datetime import timedelta
from uuid import uuid4

from django.db.models import Model, UUIDField, DateTimeField, CharField, TextField, ForeignKey, CASCADE, \
    ManyToManyField, OneToOneField, IntegerField, DurationField, SlugField

from EventType.choices import EventTypeVisibility
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
    page_slug = SlugField(max_length=255, null=True, blank=False)
    event_types = ManyToManyField(
        'EventType.EventType',
        through='MultiEventConnection',
        related_name='multi_event',
        blank=True,
        help_text="Events associated with this multi-event type."
    )

    class Meta:
        db_table = 'multi_event_type'
        verbose_name = 'Multi Event Type'
        verbose_name_plural = 'Multi Event Types'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def page_url(self):
        # note: this needs to be adjusted using user's domain or site configuration
        return f"/multi-event-types/{self.page_slug}/"


class MultiEventConnection(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    multi_event_type = ForeignKey(MultiEventType, on_delete=CASCADE, related_name='event_type_connections',
                                  related_query_name='connection')
    event_type = OneToOneField('EventType.EventType', on_delete=CASCADE,
                               limit_choices_to={'visibility': EventTypeVisibility.INHERIT},
                               related_name='multi_event_connection')
    position = IntegerField(default=0)
    buffer_before = DurationField(default=timedelta(seconds=0))

    class Meta:
        db_table = 'multi_events_connection'
        verbose_name = 'Multi Event Connection'
        verbose_name_plural = 'Multi Event Connections'
        ordering = ['multi_event_type', 'position']
        unique_together = (('multi_event_type', 'event_type'), ('multi_event_type', 'position'))

    def __str__(self):
        return f"{self.multi_event_type.name} - {self.event_type.name} (Position: {self.position})"
