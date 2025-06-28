from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class EventTypeVisibility(TextChoices):
    PUBLIC = 'public', _('Public')
    PRIVATE = 'private', _('Private')
    UNLISTED = 'unlisted', _('Unlisted')
    INHERIT = 'inherit', _('Inherit')


class EventLocationOptions(TextChoices):
    IN_PERSON = 'in-person', _('In-person')
    CALL = 'call', _('Call')
