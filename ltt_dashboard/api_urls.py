# Third Party Modules
# from django.conf.urls import url, include
from django.urls import re_path
from rest_framework.routers import DefaultRouter

from ltt_dashboard.jobs.views import JobViewSet, JobManagementViewset
from ltt_dashboard.users.views import UserAuthViewset

default_router = DefaultRouter(trailing_slash=False)

# Register all the django rest framework viewsets below.
default_router.register('jobs', JobViewSet, basename='jobs')
default_router.register('staff/jobs', JobManagementViewset, basename='jobs')
default_router.register('auth', UserAuthViewset, basename='auth')

urlpatterns = default_router.urls

