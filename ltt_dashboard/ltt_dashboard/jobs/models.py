from django.db import models

# Create your models here.

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from uuid_upload_path import upload_to

from ltt_dashboard.base.models import TimeStampedUUIDModel, Address
from ltt_dashboard.departments.models import Department
from ltt_dashboard.jobs.constants import JOB_TYPE_CHOICES, APPLICATION_STAGE_CHOICES, NEW_APPLICANT
from ltt_dashboard.users.models import User


class JobType(TimeStampedUUIDModel):
    name = models.CharField(_("Name"), max_length=100, unique=True)
    display_name = models.CharField(_("Display Name"), max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.display_name


class JobCategories(TimeStampedUUIDModel):
    name = models.CharField(max_length=100, db_index=True, unique=True)
    display_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.display_name

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
    is_remote = models.BooleanField(default=False)
    is_shown = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return self.display_name


class JobApplication(TimeStampedUUIDModel):
    job = models.ForeignKey(Job, related_name='job_application', on_delete=models.DO_NOTHING, null=False)
    user = models.ForeignKey(User, related_name='user_application', on_delete=models.DO_NOTHING, null=False)
    address = models.ForeignKey(Address, related_name='address_application', on_delete=models.DO_NOTHING, null=True,
                                blank=True)
    country = CountryField()
    email = models.EmailField(_('Email Address'), null=True, blank=True, db_index=True, )
    phone_number = models.CharField(_('phone number'), null=True, blank=True, db_index=True, max_length=15,
                                    help_text='Include the country code.')
    resume = models.FileField(_("Resume"), upload_to=upload_to, null=True, blank=True)
    applicant_message = models.TextField(_("Applicant Message"), max_length=1024, null=True, blank=True)
    last_staff_note = models.TextField(_("Latest Note By Staff"), max_length=1024, null=True, blank=True)
    application_status = models.CharField(_("Application Status"), db_index=True, choices=APPLICATION_STAGE_CHOICES,
                                          default=NEW_APPLICANT, max_length=50)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    def __str__(self):
        return "{} - {}".format(self.job.display_name, self.user.email)

    class Meta:
        unique_together = ('job', 'user')


class JobExtraField(TimeStampedUUIDModel):
    job = models.ForeignKey(Job, related_name='job_extra', on_delete=models.DO_NOTHING, null=False)
    heading = models.CharField(_("Heading"), max_length=50)
    description = models.TextField(_("Description"), max_length=1024)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.heading



