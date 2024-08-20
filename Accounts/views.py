from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
from Accounts.models import User
from .serializers import (
    RegisterSerializer, EmailVerificationSerializer, SMSVerificationSerializer, GoogleAuthenticatorSerializer, UserSerializer,LoginSerializer
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.send_verification_email()  # Automatically send email verification after user creation

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            "user": response.data,
            "message": "Registration successful! Please check your email to verify your account."
        }
        return response

class EmailVerificationView(APIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = urlsafe_base64_decode(serializer.validated_data['uid']).decode()
        token = serializer.validated_data['token']

        try:
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.email_verified = True
                user.save()
                return Response({"message": "Email successfully verified!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST)

class SMSVerificationView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SMSVerificationSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user.phone_number != serializer.validated_data['phone_number']:
            return Response({"error": "Phone number does not match"}, status=status.HTTP_400_BAD_REQUEST)

        code = serializer.validated_data['code']
        if code == user.generate_verification_code():
            user.phone_verified = True
            user.save()
            return Response({"message": "Phone number successfully verified!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)

class GoogleAuthenticatorView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GoogleAuthenticatorSerializer

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        if user.verify_google_authenticator_code(code):
            return Response({"message": "Google Authenticator verification successful!"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid Google Authenticator code"}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import LoginSerializer

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # حذف توکن قدیمی و ایجاد توکن جدید
        Token.objects.filter(user=user).delete()
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': {
                'username': user.username,
                'email': user.email,
                'verification_method': user.verification_method
            }
        }, status=status.HTTP_200_OK)
