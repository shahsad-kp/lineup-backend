from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from Authentication.apis import EmailCheckAPI, RegisterAPI, GetAuthDataAPIView, VerifyEmailOTPAPIView, ResendOTPAPIView

urlpatterns = [
    path('email-check/', EmailCheckAPI.as_view()),
    path('register/', RegisterAPI.as_view()),
    path('me/', GetAuthDataAPIView.as_view()),
    path('verify-email/', VerifyEmailOTPAPIView.as_view()),
    path('resend-code/', ResendOTPAPIView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
