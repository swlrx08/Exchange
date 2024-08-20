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
