import random
import string
from abc import ABC, abstractmethod

import requests
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import CreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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


class BaseOAuthLoginView(APIView, ABC):
    provider_name = None

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Authorization code is required'}, status=400)

        access_token = self.exchange_code_for_access_token(code)
        if not access_token:
            return Response({'error': f'Failed to exchange {self.provider_name} code for token'}, status=400)

        user_info = self.get_user_info(access_token)
        if not user_info:
            return Response({'error': f'Invalid {self.provider_name} token'}, status=400)

        user = self.get_or_create_user(user_info)
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data =  {
            'user': UserSerializer(user).data,
            'credentials': tokens,
        }
        return Response(data, status=200)

    @abstractmethod
    def exchange_code_for_access_token(self, code):
        pass

    @abstractmethod
    def get_user_info(self, access_token):
        pass

    def get_or_create_user(self, user_info):
        email = user_info['email']
        user, _ = User.objects.get_or_create(email=email, defaults={
            'full_name': user_info.get('full_name', ''),
            'email': email,
            'is_email_verified': True
        })
        return user


class GoogleLoginView(BaseOAuthLoginView):
    provider_name = "Google"

    def exchange_code_for_access_token(self, code):
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            return None
        return response.json().get('access_token')

    def get_user_info(self, access_token):
        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        response = requests.get(url, params={'access_token': access_token, 'alt': 'json'})
        if response.status_code != 200:
            return None
        data = response.json()
        return {
            'email': data.get('email'),
            'full_name': data.get('name'),
        }


class MicrosoftLoginView(BaseOAuthLoginView):
    provider_name = "Microsoft"

    def exchange_code_for_access_token(self, code):
        url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        data = {
            'code': code,
            'client_id': settings.MICROSOFT_CLIENT_ID,
            'client_secret': settings.MICROSOFT_CLIENT_SECRET,
            'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            return None
        return response.json().get('access_token')

    def get_user_info(self, access_token):
        headers = {'Authorization': f'Bearer {access_token}'}
        url = "https://graph.microsoft.com/v1.0/me"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        data = response.json()
        return {
            'email': data.get('mail') or data.get('userPrincipalName'),
            'first_name': data.get('givenName'),
            'last_name': data.get('surname'),
        }