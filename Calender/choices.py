from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class CalendarProviderChoice(TextChoices):
    GOOGLE = 'Google', _('Google')
    MICROSOFT = 'Microsoft', _('Microsoft')