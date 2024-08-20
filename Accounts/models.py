import string
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import pyotp
from twilio.rest import Client
import random
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField


characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9


# def generate_unique_id():
#     """Generates a unique 8-character ID."""
#     characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
#     while True:
#         unique_id = ''.join(random.choices(characters, k=8))
#         if not User.objects.filter(id=unique_id).exists():
#             return unique_id
        


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
    id = ShortUUIDField(unique=True,max_length=8,length=8, alphabet = characters,primary_key=True)

    email = models.EmailField(blank=True, default='', unique=True)
    name = models.CharField(max_length=255, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True, default='', unique=True)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    google_authenticator_secret = models.CharField(max_length=32, blank=True, null=True)

    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        # db_table = 'Accounts_user'  # Custom table name

    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name or self.email.split('@')[0]

    # Methods for sending email verification
    def send_verification_email(self):
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = default_token_generator.make_token(self)
        verification_link = f"http://yourdomain.com/verify/{uid}/{token}/"

        send_mail(
            "Verify your email",
            f"Please click the following link to verify your email: {verification_link}",
            "your_email@example.com",
            [self.email],
        )

    # Methods for sending SMS verification code
    def send_sms_verification_code(self):
        code = self.generate_verification_code()
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        message = client.messages.create(
            body=f"Your verification code is {code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=self.phone_number,
        )
        return code

    def generate_verification_code(self):
        return str(random.randint(100000, 999999))

    # Methods for Google Authenticator
    def generate_google_authenticator_secret(self):
        self.google_authenticator_secret = pyotp.random_base32()
        self.save()

    def get_google_authenticator_qr_code_url(self):
        totp = pyotp.TOTP(self.google_authenticator_secret)
        return totp.provisioning_uri(self.email, issuer_name="YourAppName")

    def verify_google_authenticator_code(self, code):
        totp = pyotp.TOTP(self.google_authenticator_secret)
        return totp.verify(code)

    def save(self, *args, **kwargs):
    # ابتدا بررسی کنیم که آیا رکورد در حال حاضر در پایگاه داده وجود دارد یا خیر
        if self.pk:
            try:
                old_user = User.objects.get(pk=self.pk)
                # اگر عکس پروفایل تغییر کرده است، عکس قبلی را حذف کنید
                if old_user.profile_photo != self.profile_photo:
                    if old_user.profile_photo:
                        old_user.profile_photo.delete(save=False)
            except User.DoesNotExist:
                # در صورتی که رکورد وجود نداشته باشد، این استثنا را نادیده بگیرید
                pass

        super().save(*args, **kwargs)