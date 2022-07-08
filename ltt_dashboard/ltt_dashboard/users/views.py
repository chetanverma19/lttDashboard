import jwt
from django.shortcuts import render

# Standard Library
import logging

from django.urls import reverse
from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ltt_dashboard import response
from ltt_dashboard.users.utils import Util
from .serializers import UserRegisterSerializer, UserVerificationSerializer, LoginSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class UserAuthViewset(viewsets.GenericViewSet):

    @action(detail=False, methods=['post'], url_path='register')
    def register_user(self, request):
        user = request.data
        serializer = UserRegisterSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('verify-email')
        abs_url = f"http://{current_site}{relativeLink}?token={str(token)}"
        email_body = Util.create_verify_message_for_user(user_data, abs_url)
        user_email = user_data.get('email')
        data = {
            "email_body": email_body,
            "email_subject": "Verify your account",
            "to_mail": user_email
        }
        Util.send_email(data)

        return response.Ok(data=user_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='verify-email')
    def verify_user_email(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.filter(id=payload['user_id']).first()
            if not user.is_verified:
                user.is_verified = True
                user.save()
            msg = Util.get_successful_verification_message()
            response_status = status.HTTP_200_OK
        except jwt.ExpiredSignatureError as error:
            msg = Util.get_timeout_verification_message(error)
            response_status = status.HTTP_400_BAD_REQUEST
        except jwt.exceptions.DecodeError as error:
            msg = Util.get_invalid_token_error(error)
            response_status = status.HTTP_400_BAD_REQUEST
        return response.Ok(data=msg, status=response_status)

    @action(detail=False, methods=['post'], url_path='login')
    def user_login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return response.Ok(data=serializer.data, status=status.HTTP_200_OK)
