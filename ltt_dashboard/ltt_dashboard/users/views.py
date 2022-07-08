
from django.shortcuts import render

# Standard Library
import logging
from rest_framework import generics, status

from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework import exceptions, mixins, permissions, viewsets, decorators
# farmstock Modules
from rest_framework.decorators import action

from ltt_dashboard import response
from . import serializers
from .serializers import UserRegisterSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRegisterView(generics.GenericAPIView):

    serializer_class = UserRegisterSerializer

    def post(self, request):

        user = request.data
        print('Called')
        serializer = self.serializer_class(data=user)
        print('Serialized')
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        return response.Ok(data=user_data, status=status.HTTP_201_CREATED)



# class CurrentUserViewSet(viewsets.GenericViewSet):
#     """
#     list:
#     Get current logged-in user profile
#
#     update:
#     Update current logged-in user profile
#     """
#     serializer_class = serializers.UserAuthSerializer
#     queryset = User.objects.filter(is_active=True)
#     point_param = 'point'
#     point_param_required = True
#
#     def list(self, request):
#         """Get logged in user profile"""
#         serializer = self.get_serializer(self.get_object())
#         return response.Ok(serializer.data)
#
#     def partial_update(self, request):
#         """Update logged in user profile"""
#         logger.debug("In User Partial Update")
#         logger.debug(request.data)
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return response.Ok(serializer.data)
#
#
# class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     serializer_class = serializers.SimpleUserSerializer
#     queryset = User.objects.filter(is_active=True)
#     permission_classes = (permissions.AllowAny,)
#
#     def get_queryset(self):
#         return self.queryset.select_related('address__village__block__district__state'). \
#             prefetch_related('user_topics', 'user_crops')
#
#     @decorators.action(detail=False, url_path='register-location')
#     def register_location(self, request, *args, **kwargs):
#         rl_serializer = RegisterLocationSerializer(data=request.GET, context={REQUEST_PARAM: Request(request)})
#         rl_serializer.is_valid(raise_exception=True)
#         out = rl_serializer.save()
#         return response.Ok(data=out)
#
#     @decorators.action(detail=False, methods=['post'], url_path='update-cached-details')
#     def update_user_cached_details(self, request, *args, **kwargs):
#         data = request.data
#         user_id_list = data.get('user_id_list', [])
#         is_celery_task = data.get("is_celery_task")
#         if is_celery_task:
#             update_user_id_detail_list_task.delay(user_id_list)
#         else:
#             update_user_id_detail_list(user_id_list)
#         return response.Ok()