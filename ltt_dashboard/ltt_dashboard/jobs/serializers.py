import PyPDF2
from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from django_countries import serializer_fields

from ltt_dashboard.base.serializers import AddressSerializer
from ltt_dashboard.departments.models import Department
from ltt_dashboard.departments.serializers import DepartmentSerializer
from ltt_dashboard.jobs.constants import APPLICATION_STAGE_CHOICES
from ltt_dashboard.jobs.models import Job, JobType, JobCategories, JobApplication
from ltt_dashboard.users.models import User
from ltt_dashboard.users.serializers import UserESSerializer


class JobTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobType
        fields = ['id', 'name', 'display_name']


class JobCategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobCategories
        fields = ['id', 'name', 'display_name']


class JobSerializer(serializers.ModelSerializer):

    job_type = JobTypeSerializer()
    department = DepartmentSerializer()
    categories = JobCategoriesSerializer(many=True)

    class Meta:
        model = Job
        fields = ['id', 'name', 'display_name', 'description', 'job_type', 'department', 'categories', 'is_remote']


class JobApplicationSerializer(serializers.ModelSerializer):

    job = JobSerializer()
    country = serializers.SerializerMethodField()
    resume = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'country', 'email', 'phone_number', 'resume', 'applicant_message', 'last_staff_note',
                  'application_status']

    @staticmethod
    def get_country(obj: JobApplication):
        return obj.country.name

    @staticmethod
    def get_resume(obj: JobApplication):
        return obj.resume_cloudinary_url


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
            attrs['job_type__in'] = attrs.pop('job_type')

        department_id_list = attrs.get('department')
        if department_id_list:
            query_set = Department.objects.filter(id__in=department_id_list)
            if query_set.count() != len(department_id_list):
                raise serializers.ValidationError('Invalid Department')
            attrs['department__in'] = attrs.pop('department')

        categories_id_list = attrs.get('categories')
        if categories_id_list:
            query_set = JobCategories.objects.filter(id__in=categories_id_list)
            if query_set.count() != len(categories_id_list):
                raise serializers.ValidationError('Invalid Category')
            attrs['categories__in'] = attrs.pop('categories')

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
        if not Job.objects.filter(id=attrs.get('job')).exists():
            raise serializers.ValidationError("Invalid Job ID")
        user = User.objects.filter(id=user.id).first()
        email = attrs.get('email')
        if not email:
            attrs['email'] = user.email
        return attrs


class ApplicationListRequestSerializer(serializers.Serializer):
    job = serializers.ListField(required=False)
    country = serializers.ListField(required=False)
    application_status = serializers.ListField(required=False)
    job__in = serializers.ListField(required=False)
    country__in = serializers.ListField(required=False)
    application_status__in = serializers.ListField(required=False)

    class Meta:
        fields = ['job_type__in']

    def validate(self, attrs):

        job_id_list = attrs.get('job')
        if job_id_list:
            query_set = Job.objects.filter(id__in=job_id_list)
            if query_set.count() != len(job_id_list):
                raise serializers.ValidationError('Invalid Job ID')
            attrs['job__in'] = attrs.pop('job')

        if attrs.get('country'):
            attrs['country__in'] = attrs.pop('country')

        if attrs.get('application_status'):
            attrs['application_status__in'] = attrs.pop('application_status')

        return attrs


class UpdateApplicationSerializer(serializers.Serializer):
    job = serializers.UUIDField()
    applicant = serializers.UUIDField()
    application_status = serializers.CharField()
    withhold_email = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not Job.objects.filter(id=attrs.get('job')).exists():
            raise serializers.ValidationError('Invalid Update Request')
        if not User.objects.filter(id=attrs.get('applicant')).exists():
            raise serializers.ValidationError('Invalid Update Request')
        valid_stage = False
        for stage in APPLICATION_STAGE_CHOICES:
            if stage[0] == attrs.get('application_status'):
                valid_stage = True
        if not valid_stage:
            raise serializers.ValidationError('Invalid Update Request')
        return attrs


class JobCloseRequestSerializer(serializers.Serializer):
    job = serializers.UUIDField()
    withhold_email = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not Job.objects.filter(id=attrs.get('job')).exists():
            raise serializers.ValidationError('Invalid Update Request')
        return attrs


class EntityActionSerializer(serializers.Serializer):
    entity_type = serializers.CharField()
    entity_name = serializers.CharField()
    entity_display_name = serializers.CharField()

    def validate(self, attrs):
        entity_type = attrs.get('entity_type')
        if entity_type not in ['department', 'job_type', 'job_categories']:
            raise serializers.ValidationError('Invalid Entity Type')
        return attrs


class EntityListSerializer(serializers.Serializer):
    entity_type = serializers.CharField()

    def validate(self, attrs):
        entity_type = attrs.get('entity_type')
        if entity_type not in ['department', 'job_type', 'job_categories']:
            raise serializers.ValidationError('Invalid Entity Type')
        return attrs


class JobActionSerializer(serializers.Serializer):
    name = serializers.CharField()
    display_name = serializers.CharField()
    description = serializers.CharField()
    job_type = serializers.CharField()
    department = serializers.CharField()
    categories = serializers.ListField()
    is_remote = serializers.BooleanField(required=False)
    extra_fields = serializers.ListField(required=False)

    def validate(self, attrs):
        job_type = attrs.get('job_type')
        department = attrs.get('department')
        categories_id_list = attrs.get('categories')

        if not JobType.objects.filter(id=job_type).exists():
            raise serializers.ValidationError('Invalid Job Type')
        if not Department.objects.filter(id=department).exists():
            raise serializers.ValidationError('Invalid Department')
        if categories_id_list:
            query_set = JobCategories.objects.filter(id__in=categories_id_list)
            if query_set.count() != len(categories_id_list):
                raise serializers.ValidationError('Invalid Job Categories')

        return attrs


class JobApplicationESSerializer(serializers.ModelSerializer):

    job = JobSerializer()
    user = UserESSerializer()
    country = serializers.SerializerMethodField()
    # resume = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'user', 'country', 'email', 'phone_number', 'applicant_message', 'last_staff_note',
                  'application_status']


    @staticmethod
    def get_country(obj: JobApplication):
        return obj.country.name

    # @staticmethod
    # def get_resume(obj: JobApplication):
    #     print(dir(obj.resume))
    #     # print(obj.resume.get)
    #     image_data = bytes(obj.resume.read())
    #     pdfFileObj = open(image_data, 'rb')
    #
    #     # creating a pdf reader object
    #     pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    #
    #     # printing number of pages in pdf file
    #     print(pdfReader.numPages)
    #
    #     # creating a page object
    #     pageObj = pdfReader.getPage(0)
    #
    #     # extracting text from page
    #     print(pageObj.extractText())
    #
    #     # closing the pdf file object
    #     pdfFileObj.close()
    #
    #     return ""
