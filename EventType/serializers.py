from rest_framework.serializers import ModelSerializer

from EventType.choices import EventLocationOptions
from EventType.fields import DurationInMinutesField
from EventType.models import EventType, EventTypeDurations, EventTypeLocations
from User.models import User


class EventTypeDurationsSerializer(ModelSerializer):
    duration = DurationInMinutesField()

    class Meta:
        model = EventTypeDurations
        fields = [
            'id',
            'duration',
            'is_default'
        ]


class EventTypeLocationsSerializer(ModelSerializer):
    class Meta:
        model = EventTypeLocations
        fields = [
            'id',
            'location_type',
            'is_default'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        extra_data = self.get_extra_data(instance)
        extra_data.update(self.get_extra_data(instance))
        return representation

    @staticmethod
    def get_extra_data(obj: EventTypeLocations):
        location_type = obj.location_type
        if location_type == EventLocationOptions.IN_PERSON:
            return obj.location_data.get('address', '')
        require_invitee_number = obj.location_data.get('require_invitee_number', False)
        data = {
            'require_invitee_number': require_invitee_number
        }
        if not require_invitee_number:
            phone_number = obj.location_data.get('phone_number', '')
            data['phone_number'] = phone_number
        return data


class EventTypeSerializer(ModelSerializer):
    durations = EventTypeDurationsSerializer(many=True)
    locations = EventTypeLocationsSerializer(many=True)

    class Meta:
        model = EventType
        fields = [
            'id',
            'name',
            'description',
            'owner',
            'visibility',
            'durations',
            'locations',
            'page_url'
        ]
        extra_kwargs = {
            'owner': {'read_only': True},
        }

    def create(self, validated_data: dict) -> EventType:
        durations_data = validated_data.pop('durations', [])
        locations_data = validated_data.pop('locations', [])
        user: User = self.context['request'].user

        event_type = EventType.objects.create(owner=user, **validated_data)

        for duration_data in durations_data:
            EventTypeDurations.objects.create(event_type=event_type, **duration_data)

        for location_data in locations_data:
            EventTypeLocations.objects.create(event_type=event_type, **location_data)

        return event_type
