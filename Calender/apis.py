from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from Calender.models import CalendarAccount
from Calender.serializers import CalendarAccountSerializer


class ConnectAccountView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CalendarAccountSerializer


class GetCalendarAccounts(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CalendarAccountSerializer

    def get_queryset(self):
        return CalendarAccount.objects.filter(user=self.request.user)
