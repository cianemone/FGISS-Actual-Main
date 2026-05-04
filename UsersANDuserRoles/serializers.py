from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Role, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email")

    def validate_email(self, value):
        if value and not value.endswith('@fgiss.edu'):
            raise serializers.ValidationError("Email must end with @fgiss.edu")
        return value

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = ("id", "user", "role", "phone")
