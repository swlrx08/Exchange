from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import pyotp
import random
from django.conf import settings
from twilio.rest import Client
from shortuuid.django_fields import ShortUUIDField
import string

characters = string.ascii_letters + string.digits


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = ShortUUIDField(unique=True, max_length=8, length=8, primary_key=True)
    email = models.EmailField(blank=True, default='', unique=True)
    phone_number = models.CharField(max_length=15, null=True, unique=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True, default='123')
    phone_verification_code = models.CharField(max_length=6, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def generate_verification_code(self):
        return str(random.randint(100000, 999999))

    def save(self, *args, kwargs):
        # اگر رکوردی وجود دارد و عکس پروفایل تغییر کرده، عکس قبلی حذف شود
        if self.pk:
            try:
                old_user = User.objects.get(pk=self.pk)
                if old_user.profile_photo and old_user.profile_photo != self.profile_photo:
                    old_user.profile_photo.delete(save=False)
            except User.DoesNotExist:
                pass

        super().save(*args, kwargs)
