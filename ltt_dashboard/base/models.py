# Create your models here.

# Standard Library
import uuid

# Third Party Modules
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from uuid_upload_path import upload_to
from versatileimagefield.fields import PPOIField, VersatileImageField

from ltt_dashboard.base.constants import LOCATION_TYPE_CHOICES


def custom_slugify_function(value):
    return value.replace(" ", "-")


class UUIDModel(models.Model):
    """ An abstract base class model that makes primary key `id` as UUID
    instead of default auto incremented number.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class TimeStampedUUIDModel(UUIDModel):
    """An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields with UUID as primary_key field.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class ImageMixin(models.Model):
    """An abstract base class model that provides a VersatileImageField Image with POI
    """

    image = VersatileImageField(upload_to=upload_to,
                                blank=True,
                                null=True,
                                ppoi_field='image_poi',
                                verbose_name="image")
    image_poi = PPOIField(verbose_name="image's Point of Interest")  # point of interest

    class Meta:
        abstract = True


class VideoMixin(models.Model):
    """An abstract base class model that provides the support of providing the reference of external videos
    """

    video_tag = models.CharField(_('Video Tag'), max_length=60, blank=True)
    video_url = models.URLField(_('Video URL'), blank=True)
    video_id = models.CharField(_('Video ID'), max_length=60, blank=True)
    video_source = models.CharField(_('Video Source'), max_length=60, blank=True)

    class Meta:
        abstract = True


class Country(TimeStampedUUIDModel):
    name = models.CharField(_('Name'), max_length=120)
    eng_name = models.CharField(_('English Name'), null=True, blank=True, max_length=120, db_index=True)
    slug = AutoSlugField(_('Slug'), db_index=True, populate_from=['name'], slugify_function=custom_slugify_function)
    latitude = models.DecimalField(decimal_places=5, max_digits=15, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=5, max_digits=15, blank=True, null=True)
    location = models.PointField(geography=True, default='POINT(0.0 0.0)')
    radius = models.IntegerField(_('Radius'), blank=True, null=True)

    def __str__(self):
        return self.eng_name

    def get_full_name(self):
        _all_india_name = 'भारत'
        return "{}, {}".format(self.name, _all_india_name)

    def get_eng_full_name(self):
        _all_india_name = 'India'
        return "{}, {}".format(self.eng_name, _all_india_name)

    def get_lat_lon(self):
        return self.latitude, self.longitude

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('States')


class Location(TimeStampedUUIDModel):
    name = models.CharField(_('Name'), max_length=500)
    extras = models.JSONField(_('Extras'), null=True)
    latitude = models.DecimalField(decimal_places=5, max_digits=15, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=5, max_digits=15, blank=True, null=True)
    location = models.PointField('Location', db_index=True, spatial_index=True)
    data_source = models.CharField('Data Source', max_length=200, null=True, blank=True, default=None)
    language = models.CharField('Language', max_length=5, default='hi')
    place_id = models.CharField('Place Id', max_length=500, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')


class Address(TimeStampedUUIDModel):
    address_1 = models.CharField(_('Address line 1'), max_length=100, blank=True)
    address_2 = models.CharField(_('Address line 2'), max_length=100, blank=True)
    country = models.ForeignKey(Country, blank=True, null=True, related_name='addresses', on_delete=models.CASCADE)
    location = models.PointField(null=True, blank=True, db_index=True, spatial_index=True)
    location_type = models.CharField('Location Type', max_length=100, choices=LOCATION_TYPE_CHOICES, null=True,
                                     blank=True)
    location_id = models.UUIDField('Location_Id', null=True, blank=True, db_index=True)
    extras = models.JSONField("Extras", default=dict, null=True, blank=True)

    def __str__(self):
        return '{country} - {line}'.format(country=self.country, line=self.address_1)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ('country', 'address_1')


class IPLocation(TimeStampedUUIDModel):
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True, db_index=True)
    latitude = models.DecimalField(decimal_places=5, max_digits=15, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=5, max_digits=15, blank=True, null=True)
    region_name = models.CharField(_('Region Name'), max_length=50, null=True, blank=True)
    city_name = models.CharField(_('City Name'), max_length=50, null=True, blank=True)
    extras = models.TextField(_('Description'), null=True, blank=True)

    def __str__(self):
        return '{ip_address}--{region_name}--{city_name}'.format(ip_address=self.ip_address,
                                                                 region_name=self.region_name, city_name=self.city_name)

    class Meta:
        verbose_name_plural = _('IPAddresses')

    def get_ip_location_name(self):
        return f'{self.region_name}, {self.city_name} '
