from rest_framework.viewsets import ModelViewSet

from MultiEventType.models import MultiEventType
from MultiEventType.permissions import MultiEventTypePermission


class MultiEventTypeViewSet(ModelViewSet):
    queryset = MultiEventType.objects.all()
    permission_classes = (MultiEventTypePermission,)


    def get_queryset(self):
        """
        Override the get_queryset method to filter multi-event types based on the user's permissions.
        """
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(owner=user)