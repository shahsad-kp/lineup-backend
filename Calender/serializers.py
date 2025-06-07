from typing import List

from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, DateTimeField, SerializerMethodField, ListField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from Calender.choices import CalendarProviderChoice
from Calender.exceptions import CalendarAlreadyExistsError
from Calender.integrations import GoogleCalendarAPI, MicrosoftCalendarAPI
from Calender.models import CalendarAccount, Calendar, UserCalendarSettings, Availability, \
    ConflictCalendarGroup, ConflictCalendar
from User.models import User


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


class ConflictCalendarGroupSerializer(ModelSerializer):
    calendars = SerializerMethodField()
    calendar_ids = ListField(
        child=PrimaryKeyRelatedField(queryset=Calendar.objects.all(), write_only=True),
        min_length=1,
        write_only=True,
    )

    class Meta:
        model = ConflictCalendarGroup
        fields = [
            'id',
            'calendars',
            'calendar_ids',
        ]

    def validate_calendar_ids(self, value: List[Calendar]):
        user: User = self.context["request"].user
        for cal in value:
            if cal.user != user:
                raise ValidationError('Invalid calendar id')
        return value

    def create(self, validated_data: dict):
        conflict_calendar = ConflictCalendarGroup.objects.create(
            user=self.context["request"].user,
        )
        self.create_calendars(conflict_calendar, validated_data['calendar_ids'])
        return conflict_calendar

    def update(self, instance: ConflictCalendarGroup, validated_data: dict):
        instance.conflict_calendars.all().delete()
        self.create_calendars(instance, validated_data['calendar_ids'])
        return instance

    @staticmethod
    def create_calendars(instance: ConflictCalendarGroup, calendars: List[Calendar]):
        ConflictCalendar.objects.bulk_create([
            ConflictCalendar(
                calendar=calendar,
                calendar_group=instance,
            )
            for calendar in calendars
        ])

    @staticmethod
    def get_calendars(instance: ConflictCalendarGroup) -> List[dict]:
        return CalendarSerializer(
            instance=[conflict_calendar.calendar for conflict_calendar in instance.conflict_calendars.all()],
            many=True
        ).data


class AvailabilityCalendarSerializer(ModelSerializer):
    class Meta:
        model = Availability
        fields = [
            'id',
            'created_at',
            'updated_at',
            'timezone',
            'weekly_availability',
            'individual_days_availability'
        ]


class CalendarSettingsSerializer(ModelSerializer):
    default_availability_calendar = AvailabilityCalendarSerializer()

    class Meta:
        model = UserCalendarSettings
        fields = [
            'default_event_calendar',
            'default_availability_calendar',
            'default_conflict_group'
        ]
