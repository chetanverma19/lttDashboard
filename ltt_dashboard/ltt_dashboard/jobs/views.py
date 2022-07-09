from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import permissions
from uuid_upload_path import upload_to

from ltt_dashboard import response

# Create your views here.
from ltt_dashboard.jobs.models import Job, JobApplication
from ltt_dashboard.jobs.serializers import JobSerializer, JobApplicationSerializer, JobListRequestSerializer, \
    JobCreateUpdateSerializer
from ltt_dashboard.users.models import User


class JobViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ''

    @action(detail=False, methods=['get'], url_path='test')
    def get_test_response(self, request, *args, **kwargs):
        return response.Ok(status=status.HTTP_408_REQUEST_TIMEOUT)

    @action(detail=False, methods=['post'], url_path='job-list')
    def get_list_of_jobs(self, request, *args, **kwargs):
        user = request.user
        job_filter = {
            "is_active": True,
        }
        serializer = JobListRequestSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return response.Ok(status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.data
        job_filter.update(**validated_data)
        if not user.is_staff:
            job_filter.update({"is_shown": True})
        job_list = Job.objects.filter(**job_filter).all()
        response_data = JobSerializer(job_list, many=True).data
        return response.Ok(data=response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='job-detail')
    def get_job_details(self, request):
        job_id = request.GET.get('job_id')
        job = Job.objects.filter(id=job_id).first()
        if not job:
            return response.Ok(data={"error": "Invalid Job ID"}, status=status.HTTP_400_BAD_REQUEST)
        job_data = JobSerializer(job).data
        return response.Ok(data=job_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='application-list')
    def get_list_of_own_application(self, request):
        user = request.user
        job_application_list = JobApplication.objects.filter(user__id=user.id, is_active=True).all()

        response_data = JobApplicationSerializer(job_application_list, many=True).data

        return response.Ok(data=response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'delete'], url_path='application-create-update')
    def update_user_application(self, request):
        user = request.user
        context = {'request': request}
        serializer = JobCreateUpdateSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return response.Ok(data={"error": "Invalid Application Request"}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.data
        application_job = Job.objects.filter(id=validated_data['job']).first()
        validated_data['job'] = application_job
        validated_data['user'] = User.objects.filter(id=user.id).first()
        resume = request.FILES.get('resume')
        if resume:
            validated_data['resume'] = resume
        query_set = JobApplication.objects.filter(job=application_job, user__id=user.id)
        if request.method == 'DELETE':
            if query_set.exists():
                query_set.delete()
                return response.Ok(status=status.HTTP_200_OK)
            else:
                return response.Ok(data={"error": "The application you are trying to delete does not exist for this"
                                                  "user"}, status=status.HTTP_410_GONE)

        elif query_set.exists():
            query_set.update(**validated_data)
        else:
            JobApplication.objects.update_or_create(**validated_data)
        return response.Ok(status=status.HTTP_202_ACCEPTED)





