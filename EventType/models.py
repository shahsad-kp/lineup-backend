from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db.models import Model, UUIDField, ForeignKey, CASCADE, SET_NULL, DateTimeField, CharField, DurationField, \
    BooleanField, UniqueConstraint, Q, JSONField, TextField, SlugField
from django.utils.text import slugify

from Calender.models import Calendar, Availability, ConflictCalendar
from EventType.choices import EventTypeVisibility, EventLocationOptions
from User.models import User


class EventType(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    name = CharField(max_length=255)
    description = TextField(blank=True, default='')
    owner = ForeignKey(User, on_delete=CASCADE)
    visibility = CharField(max_length=100, choices=EventTypeVisibility, default=EventTypeVisibility.PUBLIC)
    event_calendar = ForeignKey(Calendar, on_delete=SET_NULL, null=True, blank=True)
    availability_calendar = ForeignKey(Availability, on_delete=SET_NULL, null=True, blank=True)
    conflict_calendar = ForeignKey(ConflictCalendar, on_delete=SET_NULL, null=True, blank=True)
    page_slug = SlugField(max_length=255, null=True, blank=False)

    class Meta:
        db_table = 'event_type'
        verbose_name = 'Event Type'
        verbose_name_plural = 'Event Types'
        ordering = ['-created_at']
        unique_together = ('owner', 'page_slug')

    def save(self, *args, **kwargs):
        if not self.page_slug:
            base_slug = slugify(self.name)
            self.page_slug = base_slug
            counter = 1
            while EventType.objects.filter(owner=self.owner, page_slug=self.page_slug).exists():
                self.page_slug = f"{base_slug}-{counter}"
                counter += 1
        return super().save(*args, **kwargs)

    @property
    def page_url(self):
        # note: this needs to be adjusted using user's domain or site configuration
        return f"/event-type/{self.page_slug}/"

class EventTypeDurations(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    event_type = ForeignKey(EventType, on_delete=CASCADE, related_name='durations', related_query_name='ds')
    duration = DurationField()
    is_default = BooleanField(default=False)

    class Meta:
        db_table = 'event_type_duration'
        verbose_name = 'Event Type Durations'
        verbose_name_plural = 'Event Type Durations'
        ordering = ['-event_type', 'is_default', 'duration']
        constraints = [
            UniqueConstraint(
                fields=['event_type'],
                condition=Q(is_default=True),
                name='unique_default_duration_per_event_type'
            )
        ]

    def clean(self):
        if self.is_default:
            existing_default = EventTypeDurations.objects.filter(
                event_type=self.event_type,
                is_default=True
            )
            if self.pk:
                existing_default = existing_default.exclude(pk=self.pk)
            if existing_default.exists():
                raise ValidationError("Only one default duration is allowed per event type.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.duration.__str__()


class EventTypeLocations(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    event_type = ForeignKey(EventType, on_delete=CASCADE, related_name='locations', related_query_name='ls')
    location_type = CharField(max_length=100, choices=EventLocationOptions)
    location_data = JSONField(default=dict, blank=True, null=True)
    is_default = BooleanField(default=False)

    class Meta:
        db_table = 'event_type_locations'
        verbose_name = 'Event Locations'
        verbose_name_plural = 'Event Locations'
        ordering = ['event_type', 'location_type']
        constraints = [
            UniqueConstraint(
                fields=['event_type'],
                condition=Q(is_default=True),
                name='unique_default_location_per_event_type'
            )
        ]

    def clean(self):
        if self.is_default:
            existing_default = EventTypeLocations.objects.filter(
                event_type=self.event_type,
                is_default=True
            )
            if self.pk:
                existing_default = existing_default.exclude(pk=self.pk)
            if existing_default.exists():
                raise ValidationError("Only one default location is allowed per event location.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.location_type
