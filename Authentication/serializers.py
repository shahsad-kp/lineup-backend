import random
import string

from django.contrib.auth.hashers import make_password, verify_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.fields import EmailField, CharField
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from LineUp.utils.mail_utils import send_otp_email
from User.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'is_email_verified',
            'is_active',
            'timezone'
        ]


class RegisterSerializer(Serializer):
    email = EmailField(write_only=True)
    full_name = CharField(write_only=True)
    password = CharField(write_only=True)
    repeat_password = CharField(write_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + [
            'password',
            'repeat_password',
        ]

    def validate(self, attrs):
        email = attrs.get('email')
        errors = {}
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            pass
        else:
            errors['email'] = ['Email already registered']
        password = attrs.get('password')
        repeat_password = attrs.get('repeat_password')
        try:
            validate_password(password)
        except ValidationError as e:
            errors['password'] = e.messages
        if password != repeat_password:
            errors['repeat_password'] = ['Passwords must match.']
        if errors:
            raise ValidationError(errors)
        return attrs

    def create(self, validated_data: dict) -> User:
        email = validated_data.get('email')
        full_name = validated_data.get('full_name')
        password = validated_data.get('password')
        characters = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(characters, k=8))
        user = User.objects.create_user(
            email=email,
            full_name=full_name,
            password=password,
            verification_code=make_password(code),
        )
        send_otp_email(
            to_email=email,
            otp_code=code,
            user_name=full_name
        )
        return user

    def to_representation(self, instance: User) -> dict:
        refresh = RefreshToken.for_user(instance)
        credentials = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return {
            'credentials': credentials,
            'user': UserSerializer(instance).data,
        }


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {
            'user': UserSerializer(self.user).data,
            'credentials': data,
        }


class VerifyEmailSerializer(Serializer):
    code = CharField(write_only=True)

    def validate_code(self, code):
        if not self.instance:
            raise AssertionError('You can\'t verify your email without an instance')
        user: User = self.instance
        if not verify_password(code, user.verification_code)[0]:
            raise ValidationError('Incorrect code')
        return code

    def save(self, **kwargs):
        user: User = self.instance
        user.is_email_verified = True
        user.save()
        return user

    def to_representation(self, instance: User) -> dict:
        return UserSerializer(instance).data
