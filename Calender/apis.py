from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from Calender.models import CalendarAccount, Calendar, UserCalendarSettings
from Calender.permissions import CalendarAccountPermission
from Calender.serializers import CalendarAccountSerializer, CalendarAccountEditSerializer, CalendarSerializer, \
    CalendarAccountFullSerializer, CalendarSettingsSerializer


class CalendarAccountModelViewSet(ModelViewSet):
    permission_classes = [CalendarAccountPermission]
    serializer_class = CalendarAccountSerializer

    def get_queryset(self):
        queryset = CalendarAccount.objects.filter(user=self.request.user)
        if self.action == 'full_accounts':
            queryset = queryset.prefetch_related('calendars')
        return queryset

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CalendarAccountEditSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
        url_path='full_data',
    )
    def full_accounts(self, request, *args, **kwargs):
        data = CalendarAccountFullSerializer(instance=self.get_queryset(), many=True).data
        return Response(data=data)


class CalendarModelViewSet(ModelViewSet):
    permission_classes = [CalendarAccountPermission]
    serializer_class = CalendarSerializer

    def get_queryset(self):
        return Calendar.objects.filter(user=self.request.user)


class CalendarSettingsView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    serializer_class = CalendarSettingsSerializer
    permission_classes = [CalendarAccountPermission]

    def get_object(self):
        user = self.request.user
        return UserCalendarSettings.objects.get_or_create(user=user)[0]

    def get(self, *args, **kwargs):
        return self.retrieve(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.update(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.partial_update(*args, **kwargs)
