import datetime
from datetime import timedelta
from typing import Tuple

import jwt
import requests
from django.conf import settings

from Calender.choices import CalendarProviderChoice
from Calender.exceptions import CalendarAlreadyExistsError
from Calender.models import CalendarAccount
from User.models import User


class CalendarAPI:
    _refresh_token = None
    _refresh_token_expires = None
    _access_token = None
    provider: CalendarProviderChoice = None

    def __init__(self,access_token: str, refresh_token: str, refresh_token_expires: datetime,  user: User, name: str):
        self.user = user
        self.name = name
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._refresh_token_expires = refresh_token_expires

    @classmethod
    def from_code(cls, code: str, user: User, name: str = None) -> 'GoogleCalendarAPI':
        raise NotImplementedError()

    def _generate_name(self) -> str:
        raise NotImplementedError()

    def save(self):
        unique_id = self._get_unique_id()
        existing_calendar = CalendarAccount.objects.filter(unique_id=unique_id, user=self.user, provider=self.provider)
        if existing_calendar.exists():
            raise CalendarAlreadyExistsError(existing_calendar=existing_calendar.first())
        if not self.name:
            self.name = self._generate_name()
        return CalendarAccount.objects.create(
            user=self.user,
            name=self.name,
            provider=self.provider,
            refresh_token=self._refresh_token,
            refresh_token_expires=self._refresh_token_expires,
            unique_id=unique_id,
        )

    def _generate_access_token(self):
        raise NotImplementedError()

    def _get_unique_id(self) -> str:
        raise NotImplementedError()

class MicrosoftCalendarAPI(CalendarAPI):
    provider = CalendarProviderChoice.MICROSOFT

    @classmethod
    def from_code(cls, code: str, user: User, name: str = None) -> 'MicrosoftCalendarAPI':
        url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': settings.MICROSOFT_CLIENT_ID,
            'client_secret': settings.MICROSOFT_CLIENT_SECRET,
            'redirect_uri': settings.MICROSOFT_REDIRECT_URI,
            'scope': 'User.Read Calendars.ReadWrite offline_access openid'
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        data = response.json()
        return cls(
            refresh_token=data['refresh_token'],
            access_token=data['access_token'],
            refresh_token_expires=None,
            user=user,
            name=name,
        )

    def _get_profile(self) -> dict[str, str]:
        if not self._access_token:
            self._generate_access_token()
        url = 'https://graph.microsoft.com/v1.0/me'
        headers = {
            'Authorization': 'Bearer ' + self._access_token,
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data

    def _get_unique_id(self) -> str:
        return self._get_profile()['mail']

    def _generate_name(self) -> str:
        profile = self._get_profile()
        return f"{profile['displayName']} ({profile['mail']})"


class GoogleCalendarAPI(CalendarAPI):
    provider = CalendarProviderChoice.GOOGLE

    @classmethod
    def from_code(cls, code, user: User, name: str = None) -> 'GoogleCalendarAPI':
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

        refresh_token_expires = datetime.datetime.now(datetime.UTC) + timedelta(
            seconds=data['refresh_token_expires_in']
        )
        return cls(
            refresh_token=data['refresh_token'],
            access_token=data['access_token'],
            refresh_token_expires=refresh_token_expires,
            user=user,
            name=name,
        )

    def _get_profile(self) -> dict[str, str]:
        if not self._access_token:
            self._generate_access_token()
        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        response = requests.get(url, params={'access_token': self._access_token, 'alt': 'json'})
        response.raise_for_status()
        data = response.json()
        return data

    def _get_unique_id(self) -> str:
        data = self._get_profile()
        return data['id']

    def _generate_name(self) -> str:
        data = self._get_profile()
        return f"{data['name']} ({data['email']})"

    def _generate_access_token(self):
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
