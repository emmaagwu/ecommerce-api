from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


# ✅ REGISTER
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ("email", "full_name", "password", "access", "refresh", "is_staff", "is_superuser")

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            password=validated_data["password"],
        )
        refresh = RefreshToken.for_user(user)

         # Store the user instance for later access
        self.instance = user
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }


# ✅ LOGIN
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }


# ✅ USER SERIALIZER (for /auth/me/)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "is_staff", "is_superuser"]
