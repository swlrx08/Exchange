from rest_framework import serializers
from Accounts.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone_number', 'email_verified', 'phone_verified', 'google_authenticator_secret']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'name', 'phone_number', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data.get('name', ''),
            phone_number=validated_data.get('phone_number', ''),
            password=validated_data['password']
        )
        return user

class EmailVerificationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

class SMSVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

class GoogleAuthenticatorSerializer(serializers.Serializer):
    code = serializers.CharField()



from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from rest_framework.authtoken.models import Token

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        # اعتبارسنجی کاربر
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("نام کاربری یا رمز عبور نادرست است.")

        if not user.is_active:
            raise serializers.ValidationError("این حساب غیرفعال است.")

        # چک کردن وریفیکیشن بر اساس روش انتخابی کاربر
        if user.verification_method == 'email' and not user.email_verified:
            raise serializers.ValidationError("ایمیل شما هنوز تأیید نشده است.")
        if user.verification_method == 'phone' and not user.phone_verified:
            raise serializers.ValidationError("شماره تلفن شما هنوز تأیید نشده است.")
        if user.verification_method == 'google_auth' and not user.google_authenticator_enabled:
            raise serializers.ValidationError("Google Authenticator شما هنوز فعال نشده است.")

        data['user'] = user
        return data
