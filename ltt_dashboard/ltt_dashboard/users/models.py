from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from datetime import datetime

# Create your models here.
from ltt_dashboard.base.models import TimeStampedUUIDModel, ImageMixin
from ltt_dashboard.base.utils import is_empty_text


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, is_staff, is_superuser,
                     email=None, user_name=None, password=None, **extra_fields):
        if email is None:
            raise TypeError('An email must be mentioned')
        if user_name is None:
            user_name = email
        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password, user_name=None, **extra_fields):
        return self._create_user(is_staff=False, is_superuser=False,email=email,  password=password, user_name=user_name, **extra_fields)

    def create_user_through_social_auth(self, email, user_name, **extra_fields):
        return self._create_user(is_staff=False, is_superuser=False, email=email, user_name=user_name, **extra_fields)

    def create_user_through_email_password(self, email, user_name, password, **extra_fields):
        return self._create_user(is_staff=False, is_superuser=False, email=email, user_name=user_name,
                                 password=password, **extra_fields)

    def create_superuser(self, email, password, user_name=None, **extra_fields):
        return self._create_user(is_staff=True, is_superuser=True, email=email, password=password, user_name=user_name, **extra_fields)


class User(AbstractBaseUser, ImageMixin, PermissionsMixin, TimeStampedUUIDModel, models.Model):
    full_name = models.CharField(_('Full Name'), max_length=255, blank=True,
                                 help_text=_('Should include first, middle and last name. No need for title'))
    email = models.EmailField(_('email address'), db_index=True, unique=True)
    user_name = models.CharField(_('User Name'), max_length=255, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField('active', default=True, db_index=True,
                                    help_text='Designates whether this user should be treated as '
                                              'active. Unselect this instead of deleting accounts.')
    date_joined = models.DateTimeField(_('date joined'), default=datetime.now, db_index=True)
    is_verified = models.BooleanField('Is Verified', default=False, db_index=True)

    USERNAME_FIELD = 'email'
    USERNAME_FIELD_LIST_FOR_LOGIN = ['user_name', 'email']
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined',)

    def __str__(self):
        return self.email

    def tokens(self):
        return ''


class SocialAuth(TimeStampedUUIDModel):
    PROVIDER_GOOGLE = 'google'
    PROVIDER_CHOICES = [(PROVIDER_GOOGLE, _('Google'))]

    account_id = models.CharField(_('Account Id'), max_length=50, db_index=True)
    provider = models.CharField(_('Provider'), max_length=8, choices=PROVIDER_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='social_auth')
    image_url = models.CharField(_('Profile Image Url'), max_length=500, null=True, blank=True)
    extra_data = models.TextField(_('Extra Data'))

    class Meta:
        verbose_name = _('Social Auth')
        verbose_name_plural = _('Social Auths')
        unique_together = ('account_id', 'provider')
