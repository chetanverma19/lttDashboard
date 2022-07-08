from rest_framework import serializers

from ltt_dashboard.departments.serializers import DepartmentSerializer
from ltt_dashboard.jobs.models import Job, JobType, JobCategories


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
        fields = ['name', 'display_name', 'description', 'job_type', 'department', 'categories', ]
