from django.db import models

# Create your models here.

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from ltt_dashboard.base.models import TimeStampedUUIDModel
from ltt_dashboard.departments.constants import DEPARTMENT_CHOICES


class Department(TimeStampedUUIDModel):
    name = models.CharField(_("Department Name"), max_length=50, blank=False, null=False, db_index=True, unique=True)
    display_name = models.CharField('Display Text', max_length=200, unique=True)
    order = models.IntegerField(db_index=True, default=0)
    is_shown = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)
    objects = models.Manager()

    def __str__(self):
        return self.display_name
