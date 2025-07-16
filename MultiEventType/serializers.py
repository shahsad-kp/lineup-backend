from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from EventType.choices import EventTypeVisibility
from EventType.serializers import EventTypeSerializer
from LineUp.fields import DurationInMinutesField
from MultiEventType.models import MultiEventType, MultiEventConnection


class MultiEventConnectionSerializer(ModelSerializer):
    event_type = EventTypeSerializer()
    buffer_before = DurationInMinutesField()

    class Meta:
        model = MultiEventConnection
        exclude = ('multi_event_type',)

    @classmethod
    def create_connection(cls, data: dict) -> MultiEventConnection:
        event_type_data = data['event_type']
        data['event_type'] = EventTypeSerializer.create_event(event_type_data)
        multi_event_connection = MultiEventConnection.objects.create(**data)
        return multi_event_connection

    def create(self, validated_data):
        return self.create_connection(validated_data)


class MultiEventTypeSerializer(ModelSerializer):
    event_type_connections = MultiEventConnectionSerializer(many=True)

    class Meta:
        model = MultiEventType
        fields = [
            'id',
            'created_at',
            'updated_at',
            'name',
            'description',
            'owner',
            'visibility',
            'page_url',
            'event_type_connections'
        ]
        extra_kwargs = {
            'owner': {'read_only': True},
            'page_url': {'read_only': True},
        }

    @staticmethod
    def validate_event_types(event_types):
        if not isinstance(event_types, list) or len(event_types) < 2:
            raise ValidationError('At least two event types are required.')
        return event_types

    @classmethod
    def create_multi_event_type(cls, data: dict) -> MultiEventType:
        event_types_data = data.pop('event_type_connections', [])
        multi_event_type = MultiEventType.objects.create(**data)

        for event_type_data in event_types_data:
            event_type_data['event_type']['owner'] = data['owner']
            event_type_data['event_type']['visibility'] = EventTypeVisibility.INHERIT
            MultiEventConnectionSerializer.create_connection({'multi_event_type': multi_event_type, **event_type_data})

        return multi_event_type

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return self.create_multi_event_type(validated_data)
