from django.db.models import Count
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework import permissions
from django_countries.data import COUNTRIES
from uuid_upload_path import upload_to

from ltt_dashboard import response
from ltt_dashboard.departments.models import Department
from ltt_dashboard.jobs.constants import REJECTED, SELECTED, RESERVED
from ltt_dashboard.jobs.models import Job, JobApplication, JobType, JobCategories
from ltt_dashboard.jobs.serializers import JobSerializer, JobApplicationSerializer, JobListRequestSerializer, \
    JobCreateUpdateSerializer, ApplicationListRequestSerializer, UpdateApplicationSerializer, JobCloseRequestSerializer, \
    EntityActionSerializer
from ltt_dashboard.users.models import User
from ltt_dashboard.users.utils import Util

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
        job_id = request.GET.get('id')
        job = Job.objects.filter(id=job_id, is_active=True).first()
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

    @action(detail=False, methods=['get'], url_path='application-detail')
    def get_application_details(self, request):
        job_id = request.GET.get('id')
        application = JobApplication.objects.filter(job__id=job_id, user__id=request.user.id, is_active=True).first()
        if not application:
            return response.Ok(data={"error": "Invalid Job ID or No Application Found"},
                               status=status.HTTP_400_BAD_REQUEST)
        application_data = JobApplicationSerializer(application).data
        return response.Ok(data=application_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'delete'], url_path='application-create-update')
    def update_user_application(self, request):
        user = request.user
        context = {'request': request}
        serializer = JobCreateUpdateSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return response.Ok(data={"error": "Invalid Application Request"}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.data
        application_job = Job.objects.filter(id=validated_data['job'], is_active=True).first()
        application_user = User.objects.filter(id=user.id, is_active=True).first()
        validated_data['job'] = application_job
        validated_data['user'] = application_user
        resume = request.FILES.get('resume')
        if resume:
            validated_data['resume'] = resume
        query_set = JobApplication.objects.filter(job=application_job, user__id=user.id, is_active=True)
        if query_set.exists() and query_set.first().user != application_user:
            return response.Ok(status=status.HTTP_401_UNAUTHORIZED)
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


class JobManagementViewset(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser, )
    queryset = ''

    @action(detail=False, methods=['post'], url_path='application-list')
    def get_list_of_applications(self, request, *args, **kwargs):
        user = request.user
        job_filter = {
            "is_active": True,
        }
        serializer = ApplicationListRequestSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return response.Ok(status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.data
        job_filter.update(**validated_data)
        if not user.is_staff:
            job_filter.update({"is_shown": True})
        application_list = JobApplication.objects.filter(**job_filter).all()
        response_data = JobApplicationSerializer(application_list, many=True).data
        return response.Ok(data=response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='country-percentage')
    def get_country_percentage(self, request, *args, **kwargs):
        country_percentage = JobApplication.objects.all().values('country').annotate(count=Count('country'))
        for country in country_percentage:
            country['title'] = COUNTRIES[country['country']]
            country.pop('country')
        return response.Ok(data=country_percentage, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='application-status-update')
    def update_application_status(self, request, *args, **kwargs):
        serializer = UpdateApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Ok(data={"error": "Invalid Update Request"}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.data
        applicant = validated_data.get('applicant')
        applicant = User.objects.filter(id=applicant).first()
        job = validated_data.get('job')
        job = Job.objects.filter(id=job).first()
        application_status = validated_data.get('application_status')
        job_application = JobApplication.objects.filter(job=job, user=applicant).first()
        if not job_application:
            return response.Ok(status=status.HTTP_404_NOT_FOUND)
        job_application.application_status = application_status
        job_application.save()
        response_data = {
            "user": applicant.email,
            "application_status": application_status,
        }
        withhold_email = validated_data.get('withhold_email')
        if not withhold_email and application_status == REJECTED:
            email = Util.get_rejection_email(applicant.full_name, job.display_name)
            email.update({"to_mail": applicant.email})
            Util.send_email(email)
            response_data.update({"applicant_informed": True})
        return response.Ok(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='close-job')
    def close_job_opening(self, request, *args, **kwargs):
        serializer = JobCloseRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Ok(data={"error": "Invalid Job ID"}, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.data
        job = validated_data.get('job')
        job = Job.objects.filter(id=job).first()
        safe_application_status = [SELECTED, RESERVED]
        rejected_applications = JobApplication.objects.filter(job=job, is_active=True).exclude(
            application_status__in=safe_application_status)
        email = Util.get_mass_rejection_email(job.display_name)
        withhold_email = validated_data.get('withhold_email')
        rejected_applicant_email_list = []
        for rejected_application in rejected_applications:
            if rejected_application.email:
                rejected_applicant_email_list.append(rejected_application.email)
            else:
                rejected_applicant_email_list.append(rejected_application.user.email)
            rejected_application.is_active = False
            rejected_application.save()
        if not withhold_email:
            email.update({"to_mail": rejected_applicant_email_list})
            Util.send_email(email)
        return response.Ok(data={"job_status": "closed", "emails_withheld": withhold_email}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post', 'delete'], url_path='entity-action')
    def entity_action(self, request, *args, **kwargs):
        serializer = EntityActionSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Ok(status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.data
        entity_type = validated_data.get('entity_type')
        entity_name = validated_data.get('entity_name')
        entity_display_name = validated_data.get('entity_display_name')
        model = ''
        if request.method == 'DELETE':
            if entity_type == 'department':
                model = Department
            elif entity_type == 'job_type':
                model = JobType
            elif entity_type == 'job_categories':
                model = JobCategories
            model.objects.filter(name=entity_name).delete()

        if request.method == 'POST':
            if entity_type == 'department':
                model = Department
            elif entity_type == 'job_type':
                model = JobType
            elif entity_type == 'job_categories':
                model = JobCategories
            if model.objects.filter(name=entity_name).exists() or model.objects.filter(display_name=entity_display_name).exists():
                return response.Ok(data={"error": "Entity Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
            entity_obj = model.objects.create(name=entity_name, display_name=entity_display_name)
            entity_obj.save()
        return response.Ok(status=status.HTTP_200_OK)






