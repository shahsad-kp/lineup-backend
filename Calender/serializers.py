from rest_framework.fields import CharField, BooleanField
from rest_framework.serializers import ModelSerializer

from Calender.choices import CalendarProviderChoice
from Calender.exceptions import CalendarAlreadyExistsError
from Calender.integrations import GoogleCalendarAPI, CalendarAPI, MicrosoftCalendarAPI
from Calender.models import CalendarAccount


class CalendarAccountSerializer(ModelSerializer):
    code = CharField(write_only=True)

    class Meta:
        model = CalendarAccount
        fields = [
            'id',
            'name',
            'provider',
            'code',
            'connected_on',
        ]
        extra_kwargs = {
            'connected_on': {'read_only': True},
            'name': {'allow_blank': True, 'allow_null': True},
        }

    def save(self, **kwargs):
        code = self.validated_data.get('code')
        name = self.validated_data.get('name')
        provider = self.validated_data.get('provider')
        if provider == CalendarProviderChoice.GOOGLE:
            api = GoogleCalendarAPI.from_code(
                code=code,
                name=name,
                user=self.context["request"].user,
            )
        else:
            api = MicrosoftCalendarAPI.from_code(
                code=code,
                name=name,
                user=self.context["request"].user,
            )
        try:
            self.instance = api.save()
        except CalendarAlreadyExistsError as e:
            self.instance = e.existing_calendar
        return self.instance
