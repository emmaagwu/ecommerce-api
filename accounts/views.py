from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


# ✅ REGISTER
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.save()

        response = Response(
            user_data,
            status=status.HTTP_201_CREATED,
        )

        # Set HttpOnly cookie for refresh token
        response.set_cookie(
            key="refresh_token",
            value=user_data["refresh"],
            httponly=True,
            secure=True,   # 🔒 set True in production
            samesite="Lax",
            path="/",
        )
        return response


# ✅ LOGIN
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data

        response = Response(
            user_data,
            status=status.HTTP_200_OK,
        )

        # Set HttpOnly cookie for refresh token
        response.set_cookie(
            key="refresh_token",
            value=user_data["refresh"],
            httponly=True,
            secure=True,   # 🔒 True in production
            samesite="Lax",
            path="/",
        )
        return response


# ✅ LOGOUT
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token not found."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie("refresh_token", path="/api/auth/")
            return response

        except TokenError:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


# ✅ ME (Current User)
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ✅ COOKIE-BASED REFRESH
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"detail": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# ✅ ROOT ENDPOINT
@api_view(["GET"])
def auth_root(request, format=None):
    return Response({
        "register": request.build_absolute_uri(reverse("register")),
        "login": request.build_absolute_uri(reverse("login")),
        "logout": request.build_absolute_uri(reverse("logout")),
        "me": request.build_absolute_uri(reverse("me")),
        "refresh": request.build_absolute_uri(reverse("cookie_token_refresh")),
    })
