# Third Party Modules
# from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from ltt_dashboard.jobs.views import JobViewSet

default_router = DefaultRouter(trailing_slash=False)

# Register all the django rest framework viewsets below.
default_router.register('jobs', JobViewSet, basename='jobs')

urlpatterns = default_router.urls
