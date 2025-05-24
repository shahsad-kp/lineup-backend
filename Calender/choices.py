from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class CalendarProviderChoice(TextChoices):
    GOOGLE = 'Google', _('Google')
    MICROSOFT = 'Microsoft', _('Microsoft')

class CalendarAccessChoice(TextChoices):
    READER = 'reader', _('Reader')
    WRITER = 'writer', _('Writer')

class FetchStatusChoice(TextChoices):
    STARTED = 'started', _('Started')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')
    CANCELLED = 'cancelled', _('Cancelled')
