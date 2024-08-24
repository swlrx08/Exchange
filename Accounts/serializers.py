from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


# Serializer برای ارسال کد تایید ایمیل
class SendEmailVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value


# Serializer برای ارسال کد تایید شماره موبایل
class SendPhoneVerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        return value


# Serializer برای تایید کد ایمیل
class VerifyEmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)


# Serializer برای تایید کد شماره موبایل
class VerifyPhoneCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    verification_code = serializers.CharField(max_length=6)


# Serializer برای تکمیل ثبت نام
# class CompleteRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = 'all'

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User.objects.create(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user
from rest_framework import serializers
from .models import User


class CompleteRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password']

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        # The password should be set via the view, so we skip setting it here
        instance.save()
        return instance


# Serializer لاگین با ایمیل
class LoginWithEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.email_verified:
            raise serializers.ValidationError("Email is not verified.")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
        }


# Serializer لاگین با شماره موبایل
class LoginWithPhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')
        user = authenticate(phone_number=phone_number, password=password)

        if not user:
            raise serializers.ValidationError("Invalid phone number or password.")
        if not user.phone_verified:
            raise serializers.ValidationError("Phone number is not verified.")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'phone_number': user.phone_number,
            'name': user.name,
        }
