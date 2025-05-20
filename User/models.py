import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, CharField, UUIDField, BooleanField
from django.utils.translation import gettext_lazy as _

from User.managers import UserManager


class User(AbstractUser):
    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = CharField(
        _("Full Name"),
        max_length=250,
        blank=True
    )
    email = EmailField(_("Email Address"), unique=True)
    is_email_verified = BooleanField(default=False)
    timezone = CharField(
        _("Timezone"),
        max_length=150,
        blank=True
    )
    verification_code = CharField(
        _("Verification Code"),
        max_length=128,
        blank=True
    )

    objects = UserManager()

    username = None
    first_name = None
    last_name = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        db_table = "user"
