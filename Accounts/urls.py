from django.urls import path
from .views import RegisterView, EmailVerificationView, SMSVerificationView, GoogleAuthenticatorView,LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('verify-sms/', SMSVerificationView.as_view(), name='verify-sms'),
    path('verify-google-authenticator/', GoogleAuthenticatorView.as_view(), name='verify-google-authenticator'),

    path('login/', LoginView.as_view(), name='login'),
    # path('login/google-auth/', GoogleAuthenticatorVerificationView.as_view(), name='google-auth-verify'),
]
