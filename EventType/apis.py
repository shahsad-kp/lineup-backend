from rest_framework.viewsets import ModelViewSet

from EventType.choices import EventTypeVisibility
from EventType.models import EventType
from EventType.permissions import EventTypePermission
from EventType.serializers import EventTypeSerializer


class EventTypeModelViewSet(ModelViewSet):
    queryset = EventType.objects.exclude(visibility=EventTypeVisibility.INHERIT)
    permission_classes = (EventTypePermission,)
    serializer_class = EventTypeSerializer

    def get_queryset(self):
        """
        Override the get_queryset method to filter event types based on the user's permissions.
        """
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_superuser:
            return queryset
        return queryset.filter(owner=user)
