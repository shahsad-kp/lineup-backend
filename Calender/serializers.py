from rest_framework.fields import CharField, BooleanField
from rest_framework.serializers import ModelSerializer

from Calender.integrations import GoogleCalendarAPI
from Calender.models import CalendarAccount


class ConnectAccountSerializer(ModelSerializer):
    code = CharField(write_only=True)

    class Meta:
        model = CalendarAccount
        fields = [
            'id',
            'name',
            'provider',
            'code',
            'connected_on',
        ]
        extra_kwargs = {
            'connected_on': {'read_only': True},
            'name': {'allow_blank': True, 'allow_null': True},
        }

    def save(self, **kwargs):
        code = self.validated_data.get('code')
        name = self.validated_data.get('name')

        api, unique_id = GoogleCalendarAPI.from_code(
            code=code,
            name=name,
            user=self.context["request"].user,
        )
        try:
            self.instance = api.save(unique_id)
        except ValueError:
            self.instance = CalendarAccount.objects.get(unique_id=unique_id)
        return self.instance
