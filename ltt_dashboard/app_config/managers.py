# Third Party Modules
from cache_memoize import cache_memoize
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class AppVariableManager(models.Manager):

    @cache_memoize(60 * 5)
    def get_cms_related_notification_interval_time(self):
        try:
            app_variable = self.get(name="CMS_RELATED_NOTIFICATION_INTERVAL_TIME")
            return app_variable.value
        except ObjectDoesNotExist:
            return 30

