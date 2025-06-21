from rest_framework.serializers import ModelSerializer

from EventType.models import EventType, EventTypeDurations, EventTypeLocations
from User.models import User


class EventTypeDurationsSerializer(ModelSerializer):
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
            'location_data',
            'is_default'
        ]


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
