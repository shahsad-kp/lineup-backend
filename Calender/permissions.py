from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from Calender.models import CalendarAccount


class CalendarAccountPermission(IsAuthenticated):
    def has_object_permission(self, request: Request, view, obj: CalendarAccount):
        return request.user == obj.user
