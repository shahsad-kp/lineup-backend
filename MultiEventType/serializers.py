from rest_framework.serializers import ModelSerializer

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
        event_type = EventTypeSerializer.create_event(event_type_data)
        multi_event_connection = MultiEventConnection.objects.create(event_type=event_type, **data)
        return multi_event_connection

    def create(self, validated_data):
        return self.create_connection(validated_data)


class MultiEventTypeSerializer(ModelSerializer):
    event_types = MultiEventConnectionSerializer(many=True, source='event_type_connections')

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
            'event_types'
        ]

    @classmethod
    def create_multi_event_type(cls, data: dict) -> MultiEventType:
        event_types_data = data.pop('event_types', [])
        multi_event_type = MultiEventType.objects.create(**data)

        for event_type_data in event_types_data:
            MultiEventConnectionSerializer.create_connection(event_type_data | {'multi_event_type': multi_event_type})

        return multi_event_type

    def create(self, validated_data):
        return self.create_multi_event_type(validated_data)
