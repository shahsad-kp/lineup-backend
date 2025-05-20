import datetime
from datetime import timedelta
from typing import Tuple

import jwt
import requests
from django.conf import settings

from Calender.choices import CalendarProviderChoice
from Calender.models import CalendarAccount
from User.models import User


class CalendarAPI:
    def __init__(self, user: User, name: str, provider: CalendarProviderChoice, *args, **kwargs):
        self.user = user
        self.name = name
        self.provider = provider

    def from_code(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def generate_name(self) -> str:
        raise NotImplementedError()

    def save(self, *args, **kwargs) -> str:
        raise NotImplementedError()


class GoogleCalendarAPI(CalendarAPI):
    _access_token = None
    _refresh_token = None
    _expires = None
    _refresh_token_expires = None

    def __init__(self, access_token: str, refresh_token: str, refresh_token_expires: datetime, name: str, user: User):
        super().__init__(user, name, provider=CalendarProviderChoice.GOOGLE)
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._refresh_token_expires = refresh_token_expires

    @classmethod
    def from_code(cls, code, user: User, name: str = None) -> Tuple['GoogleCalendarAPI', str]:
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        data = response.json()
        id_token = data['id_token']
        decoded = jwt.decode(id_token, options={"verify_signature": False}, audience=settings.GOOGLE_CLIENT_ID)

        email = decoded.get('email')
        refresh_token_expires = datetime.datetime.now(datetime.UTC) + timedelta(
            seconds=data['refresh_token_expires_in']
        )
        return cls(
            refresh_token=data['refresh_token'],
            access_token=data['access_token'],
            refresh_token_expires=refresh_token_expires,
            user=user,
            name=name,
        ), email

    def __generate_name(self) -> str:
        if not self._access_token:
            self.__generate_access_token()
        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        response = requests.get(url, params={'access_token': self._access_token, 'alt': 'json'})
        response.raise_for_status()
        data = response.json()
        return f"{data['name']} ({data['email']})"

    def save(self, unique_id):
        if CalendarAccount.objects.filter(unique_id=unique_id, user=self.user, provider=self.provider).exists():
            raise ValueError("A calendar account with this unique id already exists")
        if not self.name:
            self.name = self.__generate_name()
        return CalendarAccount.objects.create(
            user=self.user,
            name=self.name,
            provider=self.provider,
            refresh_token=self._refresh_token,
            refresh_token_expires=self._refresh_token_expires,
            unique_id=unique_id,
        )

    def __generate_access_token(self):
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token,
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        data = response.json()
        self._access_token = data['access_token']
