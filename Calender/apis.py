from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from Calender.serializers import ConnectAccountSerializer


class ConnectAccountView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ConnectAccountSerializer
