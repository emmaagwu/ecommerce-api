from django.urls import path
from .views import RegisterView, LoginView, LogoutView, MeView, CookieTokenRefreshView, auth_root

urlpatterns = [
    path("", auth_root, name="auth_root"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("refresh/", CookieTokenRefreshView.as_view(), name="cookie_token_refresh"),
]
