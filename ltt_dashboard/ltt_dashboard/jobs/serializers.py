from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from django_countries import serializer_fields

from ltt_dashboard.base.serializers import AddressSerializer
from ltt_dashboard.departments.models import Department
from ltt_dashboard.departments.serializers import DepartmentSerializer
from ltt_dashboard.jobs.models import Job, JobType, JobCategories, JobApplication
from ltt_dashboard.users.models import User


class JobTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobType
        fields = ['name', 'display_name', 'identifier']


class JobCategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobCategories
        fields = ['name', 'display_name']


class JobSerializer(serializers.ModelSerializer):

    job_type = JobTypeSerializer()
    department = DepartmentSerializer()
    categories = JobCategoriesSerializer(many=True)

    class Meta:
        model = Job
        fields = ['name', 'display_name', 'description', 'job_type', 'department', 'categories', 'is_remote']


class JobApplicationSerializer(serializers.ModelSerializer):

    job = JobSerializer()
    country = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = ['job', 'country', 'email', 'phone_number', 'resume', 'applicant_message', 'last_staff_note',
                  'application_status']

    @staticmethod
    def get_country(obj: JobApplication):
        return obj.country.name


class JobListRequestSerializer(serializers.Serializer):
    job_type = serializers.ListField(required=False)
    department = serializers.ListField(required=False)
    categories = serializers.ListField(required=False)
    job_type__in = serializers.ListField(required=False)
    department__in = serializers.ListField(required=False)
    categories__in = serializers.ListField(required=False)
    is_remote = serializers.BooleanField(required=False)

    class Meta:
        fields = ['job_type__in']

    def validate(self, attrs):

        job_type_id_list = attrs.get('job_type')
        if job_type_id_list:
            query_set = JobType.objects.filter(id__in=job_type_id_list)
            if query_set.count() != len(job_type_id_list):
                raise serializers.ValidationError('Invalid Job Type')
            attrs.pop('job_type')
            attrs['job_type__in'] = job_type_id_list

        department_id_list = attrs.get('department')
        if department_id_list:
            query_set = Department.objects.filter(id__in=department_id_list)
            if query_set.count() != len(department_id_list):
                raise serializers.ValidationError('Invalid Department')
            attrs.pop('department')
            attrs['department__in'] = department_id_list

        categories_id_list = attrs.get('categories')
        if categories_id_list:
            query_set = JobCategories.objects.filter(id__in=categories_id_list)
            if query_set.count() != len(categories_id_list):
                raise serializers.ValidationError('Invalid Category')
            attrs.pop('categories')
            attrs['categories__in'] = categories_id_list

        return attrs


class JobCreateUpdateSerializer(serializers.ModelSerializer):

    job = serializers.UUIDField()
    country = CountryField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    resume = serializers.FileField(required=False)
    applicant_message = serializers.CharField(required=False)

    class Meta:
        model = JobApplication
        fields = ['job', 'address', 'email', 'phone_number', 'resume', 'applicant_message', 'last_staff_note',
                  'application_status', 'country']

    def validate(self, attrs):
        user = self.context.get('request').user
        if not Job.objects.filter(id=attrs['job']).exists():
            raise serializers.ValidationError("Invalid Job ID")
        user = User.objects.filter(id=user.id).first()
        email = attrs.get('email')
        if not email:
            attrs['email'] = user.email
        return attrs
