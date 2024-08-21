
from django.urls import path
from .views import (
    SendEmailVerificationCodeView,
    SendPhoneVerificationCodeView,
    VerifyEmailCodeView,
    VerifyPhoneCodeView,
    CompleteRegistrationView,
    LoginWithEmailView,
    LoginWithPhoneView
)

urlpatterns = [
    # ثبت‌نام و تایید ایمیل
    path('register/email/', SendEmailVerificationCodeView.as_view(), name='send_email_verification_code'),
    path('verify/email/', VerifyEmailCodeView.as_view(), name='verify_email_code'),

    # ثبت‌نام و تایید شماره موبایل
    path('register/phone/', SendPhoneVerificationCodeView.as_view(), name='send_phone_verification_code'),
    path('verify/phone/', VerifyPhoneCodeView.as_view(), name='verify_phone_code'),

    # تکمیل ثبت‌نام
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete_registration'),

    # لاگین با ایمیل
    path('login/email/', LoginWithEmailView.as_view(), name='login_with_email'),

    # لاگین با شماره موبایل
    path('login/phone/', LoginWithPhoneView.as_view(), name='login_with_phone'),
]
