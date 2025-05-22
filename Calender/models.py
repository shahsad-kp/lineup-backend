from uuid import uuid4

from django.db.models import Model, UUIDField, ForeignKey, CASCADE, CharField, DateTimeField
from django.db.models.fields import TextField

from Calender.choices import CalendarProviderChoice


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
        verbose_name = 'Calendar'
        verbose_name_plural = 'Calendars'

    def __str__(self):
        return self.name
