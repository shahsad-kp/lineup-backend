from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, BooleanField
from rest_framework.serializers import ModelSerializer

from LineUp.fields import DurationInMinutesField
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
    phone_number = CharField(required=False, allow_blank=True)
    address = CharField(required=False, allow_blank=True)
    require_invitee_number = BooleanField(required=False)

    class Meta:
        model = EventTypeLocations
        fields = [
            'id',
            'location_type',
            'is_default',
            'phone_number',
            'address',
            'require_invitee_number',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # extra_data = self.get_extra_data(instance)
        # extra_data.update(self.get_extra_data(instance))
        return representation


class EventTypeSerializer(ModelSerializer):
    durations = EventTypeDurationsSerializer(many=True)
    locations = EventTypeLocationsSerializer(many=True)

    def validate(self, data):
        durations = data.get('durations', [])
        locations = data.get('locations', [])

        # Validate durations: exactly one is_default=True
        default_durations = [d for d in durations if d.get('is_default') is True]
        if len(default_durations) != 1:
            raise ValidationError({
                'durations': "Exactly one duration must have is_default=True."
            })

        # Validate locations: exactly one is_default=True
        default_locations = [l for l in locations if l.get('is_default') is True]
        if len(default_locations) != 1:
            raise ValidationError({
                'locations': "Exactly one location must have is_default=True."
            })

        return data

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

    def update(self, instance: EventType, validated_data: dict) -> EventType:
        durations_data = validated_data.pop('durations', [])
        locations_data = validated_data.pop('locations', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        instance.durations.all().delete()
        EventTypeDurations.objects.bulk_create([
            EventTypeDurations(event_type=instance, **duration_data) for duration_data in durations_data
        ])

        instance.locations.all().delete()
        location_objects = []
        for location_data in locations_data:
            location_object = EventTypeLocations(event_type=instance, **location_data)
            location_object.address = location_data.get('address', '')
            location_object.require_invitee_number = location_data.get('require_invitee_number', '')
            location_object.phone_number = location_data.get('phone_number', '')
            location_objects.append(location_object)

        EventTypeLocations.objects.bulk_create(location_objects)
        return instance
