from rest_framework.viewsets import ModelViewSet

from EventType.models import EventType
from EventType.permissions import EventTypePermission
from EventType.serializers import EventTypeSerializer


class EventTypeModelViewSet(ModelViewSet):
    queryset = EventType.objects.all()
    permission_classes = (EventTypePermission,)
    serializer_class = EventTypeSerializer

    def get_queryset(self):
        """
        Override the get_queryset method to filter event types based on the user's permissions.
        """
        user = self.request.user
        if user.is_superuser:
            return EventType.objects.all()
        return EventType.objects.filter(owner=user)
