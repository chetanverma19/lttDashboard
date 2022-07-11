from rest_framework import serializers

from ltt_dashboard.base.models import Address


class AddressSerializer(serializers.ModelSerializer):

    country = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ['address_1', 'address_2', 'country', 'location', 'location_type']

    @staticmethod
    def get_country(obj: Address):
        return obj.country.eng_name