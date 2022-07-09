from django.contrib.gis import admin

# Register your models here.
from ltt_dashboard.jobs.models import JobType, JobCategories, Job, JobApplication, JobExtraField


@admin.register(JobType)
class JobTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active')
    list_editable = ('is_active', )


@admin.register(JobCategories)
class JobCategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active')
    list_editable = ('is_active',)


class JobExtraFieldAdmin(admin.TabularInline):
    model = JobExtraField
    extra = 0


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'job_type', 'department', 'is_shown', 'is_active')
    list_editable = ('is_shown', 'is_active', )
    list_filter = ('job_type__display_name', 'department__display_name', )
    filter_horizontal = ('categories', )
    search_fields = ('name', 'display_name', )
    inlines = (JobExtraFieldAdmin, )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'user', 'is_active', )
    list_editable = ('is_active', )
    list_filter = ('job', )
    search_fields = ('job__display_name', 'user__email', 'full_name', )
