import datetime
from uuid import uuid4

from django.db.models import Model, UUIDField, ForeignKey, CASCADE, CharField, DateTimeField, SET_NULL, OneToOneField, \
    IntegerField, TextField, BooleanField, JSONField
from timezone_field import TimeZoneField

from Calender.choices import CalendarProviderChoice, CalendarAccessChoice, FetchStatusChoice
from Calender.utils import week_availability_default


class CalendarAccount(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = ForeignKey('User.User', on_delete=CASCADE, related_name='calenders')
    name = CharField(max_length=250)
    provider = CharField(max_length=100, choices=CalendarProviderChoice)
    connected_on = DateTimeField(auto_now_add=True)
    refresh_token = TextField(null=True, blank=True)
    refresh_token_expires = DateTimeField(null=True, blank=True)
    unique_id = CharField(max_length=250)

    class Meta:
        db_table = 'calendar_accounts'
        verbose_name = 'Calendar Account'
        verbose_name_plural = 'Calendar Accounts'

    def __str__(self):
        return self.name


class Calendar(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    added_on = DateTimeField(auto_now_add=True)
    provider_id = CharField(max_length=250, blank=True)
    user = ForeignKey('User.User', on_delete=CASCADE, related_name='calendars')
    account = ForeignKey('CalendarAccount', on_delete=CASCADE, related_name='calendars')
    access = CharField(max_length=100, choices=CalendarAccessChoice)
    primary = BooleanField(default=False)
    name = CharField(max_length=250, blank=True)
    last_updated = ForeignKey('CalendarFetch', on_delete=SET_NULL, related_name='last_updated', null=True)

    class Meta:
        db_table = 'calendars'
        verbose_name = 'Calendar'
        verbose_name_plural = 'Calendars'
        ordering = ['-primary', '-access', '-added_on']

    def __str__(self):
        return self.name


class CalendarFetch(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    started_on = DateTimeField(auto_now_add=True)
    finished_on = DateTimeField(null=True, blank=True)
    account = ForeignKey('CalendarAccount', on_delete=CASCADE, related_name='fetches')
    sync_token = CharField(max_length=250, blank=True)
    total_pages = IntegerField(default=0)
    status = CharField(max_length=100, choices=FetchStatusChoice, default=FetchStatusChoice.STARTED)

    class Meta:
        db_table = 'calendars_fetch'
        verbose_name = 'Calendar Fetch'
        verbose_name_plural = 'Calendar Fetches'
        ordering = ['-started_on']

    def __str__(self):
        return 'Fetched on {}'.format(self.started_on)

    def complete(self, sync_token: str = None):
        self.status = FetchStatusChoice.COMPLETED
        self.finished_on = datetime.datetime.now(datetime.UTC)
        if sync_token:
            self.sync_token = sync_token
        self.save()

class ConflictCalendarGroup(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    user = ForeignKey('User.User', on_delete=CASCADE, related_name='conflict_calendars_groups')

    class Meta:
        db_table = 'conflict_calendars_groups'
        verbose_name = 'Conflict Calendar Group'
        verbose_name_plural = 'Conflict Calendar Groups'
        ordering = ['-created_at']

    def __str__(self):
        return f"Conflict Calendar Group #{self.id}"

class ConflictCalendar(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    calendar = ForeignKey('Calendar', on_delete=CASCADE, related_name='conflict_calendars')
    calendar_group = ForeignKey('ConflictCalendarGroup', on_delete=CASCADE, related_name='conflict_calendars')

    class Meta:
        db_table = 'conflict_calendars'
        verbose_name = 'Conflict Calendar'
        verbose_name_plural = 'Conflict Calendars'
        unique_together = (('calendar', 'calendar_group'),)

class Availability(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    user = ForeignKey('User.User', on_delete=CASCADE, related_name='availabilities')
    timezone = TimeZoneField()
    weekly_availability = JSONField(default=week_availability_default)
    individual_days_availability = JSONField(default=dict)

    class Meta:
        db_table = 'availability'
        verbose_name = 'Availability'
        verbose_name_plural = 'Availabilities'
        ordering = ['-user']

    def __str__(self):
        return f"{self.user} on {self.created_at}"


class UserCalendarSettings(Model):
    id = UUIDField(primary_key=True, default=uuid4, editable=False)
    user = OneToOneField('User.User', on_delete=CASCADE, related_name='calendar_settings')
    default_event_calendar = ForeignKey(
        'Calendar',
        on_delete=SET_NULL,
        related_name='default_event_calendar',
        null=True
    )
    default_availability_calendar = ForeignKey(
        'Availability',
        on_delete=SET_NULL,
        related_name='default_availability_calendar',
        null=True
    )
    default_conflict_group = ForeignKey(
        'ConflictCalendarGroup',
        on_delete=SET_NULL,
        related_name='default_conflict_group',
        null=True
    )

    class Meta:
        db_table = 'user_calendar_settings'
        verbose_name = 'User Calendar Settings'
        verbose_name_plural = 'User Calendar Settings'
