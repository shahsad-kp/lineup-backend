from datetime import timedelta

from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field


class DurationInMinutesField(Field):
    def to_representation(self, value):
        return int(value.total_seconds() / 60)

    def to_internal_value(self, data):
        try:
            minutes = int(data)
            return timedelta(minutes=minutes)
        except (ValueError, TypeError):
            raise ValidationError("Invalid duration in minutes.")
