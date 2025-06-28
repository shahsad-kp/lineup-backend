from django.db.models.enums import TextChoices


class MultiEventVisibility(TextChoices):
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'
    UNLISTED = 'unlisted', 'Unlisted'