from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

from EventType.choices import EventTypeVisibility
from EventType.models import EventType


class EventTypePermission(BasePermission):
    def has_permission(self, request: Request, view: ViewSet):
        if view.action not in ['list', 'retrieve']:
            return bool(request.user and request.user.is_authenticated)
        return True

    def has_object_permission(self, request: Request, view: ViewSet, obj: EventType):
        if obj.owner == request.user:
            return True
        if view.action in ['list', 'retrieve']:
            return obj.visibility == EventTypeVisibility.PUBLIC
        return False
