# Third Party Modules

from django.contrib import admin

from ltt_dashboard.app_config.models import AppVariable


class AppVariableReleaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'description', 'value', 'modified_at')
    search_fields = ('name', 'display_name')
    readonly_fields = ('id', 'created_at', 'modified_at')
    save_as = True


admin.site.register(AppVariable, AppVariableReleaseAdmin)

