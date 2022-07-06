from django.contrib.gis import admin

# Register your models here.
from ltt_dashboard.base.models import Location, IPLocation, Address, Country


@admin.register(Address)
class AddressAdmin(admin.OSMGeoAdmin):
    list_display = ('id', 'country', 'created_at')
    list_filter = ('created_at', 'modified_at')
    search_fields = ('address_1', 'address_2', 'pincode', 'village__name')
    readonly_fields = ('id', 'created_at', 'modified_at')
    raw_id_fields = ('country',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'place_id')
    list_filter = ('data_source',)


@admin.register(IPLocation)
class IPLocationAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'latitude', 'longitude', 'region_name', 'city_name')
    search_fields = ('ip_address',)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'eng_name')
    search_fields = ('name', 'eng_name')