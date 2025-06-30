from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet

from MultiEventType.choices import MultiEventVisibility
from MultiEventType.models import MultiEventType


class MultiEventTypePermission(BasePermission):
    def has_permission(self, request: Request, view: ViewSet):
        if view.action not in ['list', 'retrieve']:
            return bool(request.user and request.user.is_authenticated)
        return True

    def has_object_permission(self, request: Request, view: ViewSet, obj: MultiEventType):
        if view.action in ['list', 'retrieve']:
            return obj.visibility == MultiEventVisibility.PUBLIC
        return obj.owner_id == request.user.id