import random
import string

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import CreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from Authentication.serializers import RegisterSerializer, UserSerializer, VerifyEmailSerializer
from LineUp.utils.mail_utils import send_otp_email
from User.models import User


class EmailCheckAPI(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request: Request, *_, **__):
        email = request.data.get('email')
        if email is None:
            return Response({'error': 'No email provided'}, status=400)
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response({'error': 'No such user'}, status=404)
        else:
            return Response({'email': user.email}, status=200)


class RegisterAPI(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class GetAuthDataAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class VerifyEmailOTPAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyEmailSerializer

    def post(self, request: Request, *_, **__):
        serializer = self.get_serializer(data=request.data, instance=self.get_object())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_object(self):
        return self.request.user

class ResendOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def patch(request: Request, *_, **__):
        user = request.user
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(characters, k=8))
        send_otp_email(
            to_email=user.email,
            otp_code=code,
            user_name=user.full_name,
        )
        user.verification_code = make_password(code)
        user.save()
        return Response({'detail': 'Code sent successfully'}, status=200)
