# Third Party Modules
from django.db import models
from django.utils.translation import gettext_lazy as _

from ltt_dashboard.app_config.managers import AppVariableManager
from ltt_dashboard.base.models import TimeStampedUUIDModel


class AppVariable(TimeStampedUUIDModel):
    name = models.CharField(_('variable name'), max_length=128, unique=True)
    display_name = models.CharField(_('variable display name'), max_length=256)
    description = models.CharField(_('variable description'), max_length=1024)
    value = models.CharField(_('variable value'), max_length=256)
    detailed_value = models.TextField(_('Detailed Value'), null=True, blank=True)
    objects = AppVariableManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'App Variable'
        verbose_name_plural = 'App Variables'
