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

    @staticmethod
    def update_connection(instance: MultiEventConnection, validated_data: dict) -> MultiEventConnection:
        instance.buffer_before = validated_data.get('buffer_before', instance.buffer_before)
        instance.position = validated_data.get('position', instance.position)
        instance.save()
        return instance

    def create(self, validated_data):
        return self.create_connection(validated_data)

    def update(self, instance, validated_data):
        return self.update_connection(instance, validated_data)


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

    @staticmethod
    def update_multi_event_type(instance: MultiEventType, validated_data: dict) -> MultiEventType:
        event_types_data = validated_data.pop('event_type_connections', [])
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.save()

        # Update connections
        for event_type_data in event_types_data:
            connection_id = event_type_data.get('id')
            if connection_id:
                connection = MultiEventConnection.objects.get(id=connection_id, multi_event_type=instance)
                MultiEventConnectionSerializer.update_connection(connection, event_type_data)
            else:
                MultiEventConnectionSerializer.create_connection({'multi_event_type': instance, **event_type_data})
        return instance

    def create(self, validated_data: dict) -> MultiEventType:
        validated_data['owner'] = self.context['request'].user
        return self.create_multi_event_type(validated_data)

    def update(self, instance: MultiEventType, validated_data: dict) -> MultiEventType:
        return self.update_multi_event_type(instance, validated_data)
