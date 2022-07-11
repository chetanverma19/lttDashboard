# Third Party Modules
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed

from ltt_dashboard.users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'user_name', 'email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        user_name = attrs.get('user_name', '')

        if not user_name.isalnum():
            raise serializers.ValidationError('Username should only contain alphanumeric character')

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=64, min_length=6, write_only=True)
    user_name = serializers.CharField(max_length=64, min_length=6, read_only=True)
    tokens = serializers.JSONField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'user_name', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')

        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')

        if not user.is_verified:
            raise AuthenticationFailed('Please verify account through the link in your email')

        return {
            "email": user.email,
            "user_name": user.user_name,
            "tokens": user.tokens()
        }


class UserESSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'user_name', 'is_staff', 'is_active', 'date_joined', 'is_verified']
