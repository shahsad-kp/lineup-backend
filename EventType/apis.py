from rest_framework.viewsets import ModelViewSet

from EventType.models import EventType
from EventType.permissions import EventTypePermission
from EventType.serializers import EventTypeSerializer


class EventTypeModelViewSet(ModelViewSet):
    queryset = EventType.objects.all()
    permission_classes = (EventTypePermission,)
    serializer_class = EventTypeSerializer
