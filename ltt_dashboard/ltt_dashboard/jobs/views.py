from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import permissions

from ltt_dashboard import response

# Create your views here.
from ltt_dashboard.jobs.models import Job
from ltt_dashboard.jobs.serializers import JobSerializer


class JobViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ''

    @action(detail=False, methods=['get'], url_path='test')
    def get_test_response(self, request, *args, **kwargs):
        return response.Ok(status=status.HTTP_408_REQUEST_TIMEOUT)

    @action(detail=False, methods=['post'], url_path='job-list')
    def get_list_of_jobs(self, request, *args, **kwargs):
        job_filter = {
            "is_active": True,
        }

        user = request.user
        if not user.is_staff:
            job_filter.update({"is_shown": True})

        job_list = Job.objects.filter(**job_filter).all()

        response_data = JobSerializer(job_list, many=True).data

        return response.Ok(data=response_data, status=status.HTTP_200_OK)
