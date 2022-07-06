from django.contrib.gis import admin

# Register your models here.
from ltt_dashboard.departments.models import Department


@admin.register(Department)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'identifier', 'order', 'is_active', )
    list_filter = ('is_active', )
    list_editable = ('order', 'is_active', )
    search_fields = ('name', 'display_name', 'identifier', )
    readonly_fields = ('id', 'created_at', 'modified_at', )
