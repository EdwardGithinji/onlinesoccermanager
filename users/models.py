import jwt
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model to override the builtin auth.User model
    """

    first_name = models.CharField(_('first name'), max_length=150, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    is_email_verified = models.BooleanField(_('verified email'), default=False)
    profile_photo = models.ImageField(upload_to='profile_pics', null=True, blank=True)
    is_staff: bool = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active: bool = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), default=timezone.now)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_completed = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return ' '.join(filter(None, (self.first_name, self.last_name)))

    @property
    def is_team_owner(self) -> bool:
        return hasattr(self, 'team')

    @property
    def token(self):
        valid_minutes: int = getattr(settings, "JWT_VALIDITY_MINUTES", 60)
        expiry_date = datetime.now() + timedelta(minutes=valid_minutes)
        algorithm: str = getattr(settings, "JWT_ALGORITHM", 'HS256')

        token_payload = {
            'id': self.pk,
            'exp': int(expiry_date.strftime('%s')),
            "email": self.email
        }

        return jwt.encode(token_payload, settings.SECRET_KEY, algorithm=algorithm)
