from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _


class SetupProgressChoices(IntegerChoices):
    CONNECT_ACCOUNTS = 0, _('Connect Accounts')
    EVENT_CALENDAR = 1, _('Event Calendar')
    CONFLICT_CALENDAR = 2, _('Conflict Calendar')
    AVAILABILITY_CALENDAR = 3, _('Availability Calendar')
    COMPLETED = 4, _('Completed')
