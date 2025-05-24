from rest_framework.fields import CharField, DateTimeField, SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Calender.choices import CalendarProviderChoice
from Calender.exceptions import CalendarAlreadyExistsError
from Calender.integrations import GoogleCalendarAPI, MicrosoftCalendarAPI
from Calender.models import CalendarAccount, Calendar, UserCalendarSettings


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
            api.fetch_calendars()
        except CalendarAlreadyExistsError as e:
            self.instance = e.existing_calendar
        return self.instance


class CalendarAccountEditSerializer(ModelSerializer):
    class Meta:
        model = CalendarAccount
        fields = [
            'id',
            'name',
            'provider',
            'connected_on',
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'connected_on': {'read_only': True},
            'provider': {'read_only': True},
        }


class CalendarSerializer(ModelSerializer):
    last_updated = DateTimeField(read_only=True, source='last_updated.started_on')
    provider = CharField(read_only=True, source='account.provider')

    class Meta:
        model = Calendar
        fields = [
            'id',
            'name',
            'access',
            'primary',
            'last_updated',
            'provider'
        ]


class CalendarAccountFullSerializer(ModelSerializer):
    calendars = CalendarSerializer(many=True, read_only=True)
    last_updated = SerializerMethodField()

    class Meta:
        model = CalendarAccount
        fields = [
            'id',
            'name',
            'provider',
            'connected_on',
            'last_updated',
            'calendars'
        ]

    @staticmethod
    def get_last_updated(obj: CalendarAccount):
        return obj.fetches.all().first().started_on


class CalendarSettingsSerializer(ModelSerializer):
    class Meta:
        model = UserCalendarSettings
        fields = [
            'default_event_calendar'
        ]
