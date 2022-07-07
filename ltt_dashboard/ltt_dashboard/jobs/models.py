from django.db import models

# Create your models here.

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from ltt_dashboard.base.models import TimeStampedUUIDModel
from ltt_dashboard.departments.models import Department
from ltt_dashboard.jobs.constants import JOB_TYPE_CHOICES


class JobType(TimeStampedUUIDModel):
    name = models.CharField(_("Name"), max_length=100)
    display_name = models.CharField(_("Display Name"), max_length=100)
    identifier = models.CharField(_("Identifier"), max_length=50, choices=JOB_TYPE_CHOICES, null=False)
    is_active = models.BooleanField(default=True)


class JobCategories(TimeStampedUUIDModel):
    name = models.CharField(max_length=100, db_index=True, unique=True)
    display_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'


class Job(TimeStampedUUIDModel):
    name = models.CharField(_("Name"), max_length=100, db_index=True)
    display_name = models.CharField(_("Display Name"), max_length=100)
    description = models.TextField(_("Description"), max_length=1024)
    job_type = models.ForeignKey(JobType, related_name='job_type', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, related_name='job_type', on_delete=models.SET_NULL, null=True,
                                   blank=True)
    categories = models.ManyToManyField(JobCategories, related_name='job_type', null=True, blank=True)
    is_shown = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

