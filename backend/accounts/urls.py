from django.urls import path

from .views import (CookieTokenRefreshAPIView,CsrfTokenAPIView,LoginAPIView,LogoutAPIView,SignupView,)

urlpatterns = [
    path("csrf/", CsrfTokenAPIView.as_view(), name="csrf-token"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("token/refresh/", CookieTokenRefreshAPIView.as_view(), name="token-refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]