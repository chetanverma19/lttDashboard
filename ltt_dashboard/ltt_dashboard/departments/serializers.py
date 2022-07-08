from rest_framework import serializers

from ltt_dashboard.departments.models import Department


class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ['name', 'display_name', 'identifier', ]
