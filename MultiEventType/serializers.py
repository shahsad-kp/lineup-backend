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
