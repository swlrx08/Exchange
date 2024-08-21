# views.py

from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    SendEmailVerificationCodeSerializer,
    SendPhoneVerificationCodeSerializer,
    VerifyEmailCodeSerializer,
    VerifyPhoneCodeSerializer,
    CompleteRegistrationSerializer,
    LoginWithEmailSerializer,
    LoginWithPhoneSerializer
)

# ویوی ارسال کد تایید ایمیل
class SendEmailVerificationCodeView(generics.GenericAPIView):
    serializer_class = SendEmailVerificationCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        user, created = User.objects.get_or_create(email=email)
        # verification_code = user.generate_verification_code()
        # #______________________________________________________
        # user.email_verification_code = verification_code
        user.save()

        # send_mail(
        #     "Email Verification",
        #     f"Your verification code is {verification_code}",
        #     "your_email@example.com",
        #     [email],
        # )

        return Response({"detail": "Verification code sent to email."}, status=status.HTTP_200_OK)

# ویوی ارسال کد تایید شماره موبایل
class SendPhoneVerificationCodeView(generics.GenericAPIView):
    serializer_class = SendPhoneVerificationCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data.get('phone_number')
        user, created = User.objects.get_or_create(phone_number=phone_number)
        verification_code = user.generate_verification_code()
        user.phone_verification_code = verification_code
        user.save()

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Your verification code is {verification_code}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number,
        )

        return Response({"detail": "Verification code sent to phone."}, status=status.HTTP_200_OK)

# ویوی تایید کد ایمیل
class VerifyEmailCodeView(generics.GenericAPIView):
    serializer_class = VerifyEmailCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        verification_code = serializer.validated_data.get('verification_code')

        try:
            user = User.objects.get(email=email)
            if user.email_verification_code == verification_code:
                user.email_verified = True
                user.save()
                return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# ویوی تایید کد شماره موبایل
class VerifyPhoneCodeView(generics.GenericAPIView):
    serializer_class = VerifyPhoneCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data.get('phone_number')
        verification_code = serializer.validated_data.get('verification_code')

        try:
            user = User.objects.get(phone_number=phone_number)
            if user.phone_verification_code == verification_code:
                user.phone_verified = True
                user.save()
                return Response({"detail": "Phone number verified successfully."}, status=status.HTTP_200_OK)
            return Response({"detail": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# ویوی تکمیل ثبت نام (برای هر دو حالت ایمیل و شماره موبایل)
# class CompleteRegistrationView(generics.GenericAPIView):
#     serializer_class = CompleteRegistrationSerializer

#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         phone_number = request.data.get('phone_number')

#         if email:
#             try:
#                 user = User.objects.get(email=email)
#                 if not user.email_verified:
#                     return Response({"detail": "Email not verified."}, status=status.HTTP_400_BAD_REQUEST)
#             except User.DoesNotExist:
#                 return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
#         if phone_number:
#             try:
#                 user = User.objects.get(phone_number=phone_number)
#                 if not user.phone_verified:
#                     return Response({"detail": "Phone number not verified."}, status=status.HTTP_400_BAD_REQUEST)
#             except User.DoesNotExist:
#                 return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()

#         # Generate JWT token
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "detail": "Registration completed successfully."
#         }, status=status.HTTP_201_CREATED)


class CompleteRegistrationView(generics.GenericAPIView):
    serializer_class = CompleteRegistrationSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')  # Get the password from the request

        # Check if the user exists and whether email/phone verification is complete
        if email:
            try:
                user = User.objects.get(email=email)
                if not user.email_verified:
                    return Response({"detail": "Email not verified."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
                if not user.phone_verified:
                    return Response({"detail": "Phone number not verified."}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate the request data with the serializer
        serializer = self.serializer_class(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Set the password using Django's `set_password` method
        user.set_password(password)
        user.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "detail": "Registration completed successfully."
        }, status=status.HTTP_201_CREATED)


# ویوی لاگین با ایمیل
class LoginWithEmailView(generics.GenericAPIView):
    serializer_class = LoginWithEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# ویوی لاگین با شماره موبایل
class LoginWithPhoneView(generics.GenericAPIView):
    serializer_class = LoginWithPhoneSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
