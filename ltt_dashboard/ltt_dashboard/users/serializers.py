# Third Party Modules
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ltt_dashboard.users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['user_name', 'email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        user_name = attrs.get('user_name', '')

        if not user_name.isalnum():
            raise serializers.ValidationError('Username should only contain alphanumeric character')

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)




# from firebase_admin import auth
#
# from farmstock import base, fa_logger
# # farmstock Modules
# from farmstock.base.models import Address, Crop, Topic, Village, DefaultImage
# from farmstock.base.serializers import (
#     AddressSerializer,
#     CropSerializer,
#     NullableVersatileImageFieldSerializer,
#     TopicSerializer,
#     BlockSerializer, DistrictSerializer, StateSerializer, CropLeanSerializer, TopicLeanSerializer,
#     CropWithoutCropTypeSerializer)
# from farmstock.base.services import LocationService, get_shortern_id, default_location, get_trimmed_location_name
# from farmstock.generic_utills.request import REQUEST_PARAM, Request
# from farmstock.shop.partner.services import get_partner
# from farmstock.user_network.service import get_leader_count
# from farmstock.users import UserDesignation
# from .constants import DESIGNATION_DISPLAY_CHOICES_SHOW, DESIGNATION_DISPLAY_CHOICES_NOT_SHOW
# from .models import UserCrop, UserTopic, DerivedAddress, UserRating, UserPhoneBook, UserCoverImage, Designation, \
#     UserGeoLocation, UserIdShortner, UserSpammerInfo, UserProfession, UserProfessionMapping
# from ..celery_pub_sub.publisher import publish
# from ..generic_utills.format_string import is_empty_text
# from ..generic_utills.serializer_util import UUIDListField
# from ..listing.services.common_services.util import is_admin
# from ..user_network.models import UserReferral, UserNetworkStat
# from farmstock.users.services.user_location_service import UserLocationService
# from ..user_stages.constant import UserStageName
# from farmstock.constants.celery_pub_sub_topics import Topic as ps_topic
#
# User = get_user_model()
#
#
# class DesignationSerializer(serializers.ModelSerializer):
#     image = NullableVersatileImageFieldSerializer(sizes='content_image', required=False)
#     badge_image = NullableVersatileImageFieldSerializer(sizes='content_image', required=False)
#     name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Designation
#         fields = ['id', 'image', 'eng_name', 'name', 'badge_color', 'badge_icon', 'badge_image_reference',
#                   'badge_image',
#                   'namespace']
#
#     def get_name(self, obj):
#         if obj.eng_name == UserDesignation.SPAMMER:
#             return ''
#         else:
#             return obj.name
#
#
# class RegisterLocationSerializer(serializers.Serializer):
#     point = serializers.RegexField('^(-?\\d+(\\.\\d+)?),\\s*(-?\\d+(\\.\\d+)?)$', required=True)
#
#     def create(self, validated_data):
#         request: Request = self.context.get(REQUEST_PARAM)
#         lat, lon, location_name = LocationService().get_location_by_point(validated_data['point'])
#         point = LocationService.get_point(lat, lon)
#         if request.user and lat and lon:
#             da = UserGeoLocation.objects.update_or_create(
#                 user=request.user,
#                 defaults={
#                     'latitude': lat,
#                     'longitude': lon,
#                     'location': point,
#                     'location_name': location_name
#                 }
#             )
#             return {"id": str(da[0].id)}
#         return ""
#
#
# class SimpleUserSerializer(serializers.ModelSerializer):
#     image = NullableVersatileImageFieldSerializer(sizes='user_image')
#     address = AddressSerializer()
#     designation_display_name = serializers.SerializerMethodField()
#     derived_address = serializers.SerializerMethodField()
#     description = serializers.SerializerMethodField()
#     location_text = serializers.SerializerMethodField()
#
#     class Meta:
#         ref_name = 'UserModule'
#         model = User
#         fields = ['id', 'full_name', 'bio', 'image', 'address', 'derived_address', 'user_type', 'designation',
#                   'designation_display_name', 'description', 'is_verified', 'location_text']
#
#     def get_designation_display_name(self, obj):
#         return UserDesignation.display_name.get(obj.designation)
#
#     def get_designation(self, obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             return user_designation.eng_name
#         else:
#             return UserDesignation.NORMAL_USER
#
#     def get_derived_address(self, obj):
#         derived_address_qs = DerivedAddress.objects.filter(~Q(block=None), user=obj, is_active=True).first()
#         if derived_address_qs:
#             return DerivedAddressSerializer(derived_address_qs, context=self.context).data
#         else:
#             return None
#
#     @staticmethod
#     def _get_district_display_name(address):
#         try:
#             district = address.village.block.district
#             state = district.state
#             return "%s, %s" % (district.name, state.name)
#         except:
#             return ""
#
#     @staticmethod
#     def _get_block_display_name(address):
#         try:
#             district = address.block.district
#             state = district.state
#             return "%s, %s" % (district.name, state.name)
#         except:
#             return ""
#
#     def get_description(self, obj):
#         _user_description = ""
#         if obj.designation and obj.designation in UserDesignation.SPECIAL_USERS:
#             _user_description = UserDesignation.display_name[obj.designation]
#         if not _user_description:
#             _user_description = self._get_district_display_name(obj.address)
#
#         if not _user_description:
#             try:
#                 _user_description = self._get_block_display_name(obj.derived_addresses)
#             except:
#                 pass
#
#         return _user_description
#
#     def get_location_text(self, obj):
#         try:
#             _, _, _, location_text = UserLocationService(user=obj).get_location_from_user_instance()
#             fa_logger.debug("user id {} and location text {}".format(str(obj.id), location_text))
#             location_text_list = location_text.split(',')
#             if len(location_text_list) >= 3:
#                 location_text = location_text_list[1] + ',' + location_text_list[2]
#             return location_text
#         except Exception as e:
#             fa_logger.error(e)
#         return None
#
#
# class BasicUserSerializer(serializers.ModelSerializer):
#     image = NullableVersatileImageFieldSerializer(sizes='user_image')
#     designation_display_name = serializers.SerializerMethodField()
#     designation = serializers.SerializerMethodField()
#     # user_designation = DesignationSerializer()
#     user_designation = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ['id', 'full_name', 'bio', 'image', 'user_type', 'designation', 'designation_display_name',
#                   'user_designation', 'is_verified']
#
#     def get_designation_display_name(self, obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             choice = user_designation.designation_display_choice
#             if choice == DESIGNATION_DISPLAY_CHOICES_SHOW:
#                 return user_designation.name
#         return ""
#
#     def get_designation(self, obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             return user_designation.eng_name
#         else:
#             return UserDesignation.NORMAL_USER
#
#     def get_user_designation(self, obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             choice = user_designation.designation_display_choice
#             if choice == DESIGNATION_DISPLAY_CHOICES_SHOW:
#                 return DesignationSerializer(user_designation).data
#         return None
#
#
# class BasicUserContactInfoSerializer(BasicUserSerializer):  # Todo Send contact info via some encryption
#     class Meta(BasicUserSerializer.Meta):
#         model = User
#         fields = BasicUserSerializer.Meta.fields + ['phone_number', 'email']
#
#
# class UserCoverImageSerializer(serializers.ModelSerializer):
#     image = NullableVersatileImageFieldSerializer(sizes='content_image', required=False)
#
#     class Meta:
#         model = UserCoverImage
#         fields = ('image',)
#
#
# class DesignationImageSerializer(serializers.ModelSerializer):
#     image = NullableVersatileImageFieldSerializer(sizes='content_image', required=False)
#
#     class Meta:
#         model = Designation
#         fields = ('image',)
#
#
# class UserSerializer(serializers.ModelSerializer):
#     image = NullableVersatileImageFieldSerializer(sizes='user_image', required=False)
#     address = AddressSerializer(required=False)
#     topics = TopicSerializer(many=True)
#     crops = CropWithoutCropTypeSerializer(many=True)
#     topic_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True,
#                                       min_length=0, max_length=100, required=False)
#     crop_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True,
#                                      min_length=0, max_length=100, required=False)
#     village_id = serializers.UUIDField(required=False, write_only=True)
#
#     leader_count = serializers.SerializerMethodField()
#
#     follower_count = serializers.SerializerMethodField()
#     designation_display_name = serializers.SerializerMethodField()
#     user_designation = serializers.SerializerMethodField()
#     cover_image = serializers.SerializerMethodField()
#     derived_address = serializers.SerializerMethodField()
#     description = serializers.SerializerMethodField()
#     partner = serializers.SerializerMethodField()
#     is_channel = serializers.SerializerMethodField()
#     referral_code = serializers.SerializerMethodField()
#     is_referred = serializers.SerializerMethodField()
#     business_profile = serializers.SerializerMethodField()
#     address_info = serializers.JSONField(required=False, write_only=True)
#     location_id = serializers.UUIDField(required=False, write_only=True)
#     location_type = serializers.CharField(required=False, write_only=True)
#     location_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = User
#         fields = ['id', 'full_name', 'phone_number', 'is_phone_number_public', 'user_type', 'designation',
#                   'designation_display_name', 'bio', 'image', 'address', 'date_joined', 'onboarded_at', 'topics',
#                   'crops', 'topic_ids',
#                   'crop_ids', 'village_id', "leader_count", "follower_count", "cover_image", "derived_address",
#                   "description", "user_designation", "is_verified", "partner", "is_channel", 'referral_code',
#                   'is_referred', 'business_profile', "address_info", "location_id", "location_type", "location_name"]
#         read_only_fields = ('phone_number', 'id', 'date_joined',
#                             'address', 'topics', 'crops', 'referral_code', 'is_referred')
#
#     @staticmethod
#     def get_referral_code(obj):
#         user_id_shortner_obj = UserIdShortner.objects.filter(user=obj).first()
#         if user_id_shortner_obj:
#             numeric_id = user_id_shortner_obj.numeric_id
#             short_id = get_shortern_id(numeric_id)
#             return short_id
#         return None
#
#     @staticmethod
#     def get_is_referred(obj):
#         return UserReferral.objects.filter(user=obj).first() is not None
#
#     @staticmethod
#     def get_leader_count(obj):
#         network_stat = obj.user_network_stat.first()
#         return network_stat.following_count + 3 if network_stat else 0
#
#     @staticmethod
#     def get_follower_count(obj):
#         network_stat = obj.user_network_stat.first()
#         return network_stat.follower_count if network_stat else 0
#
#     @staticmethod
#     def get_designation_display_name(obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             return user_designation.name
#         else:
#             return UserDesignation.display_name[UserDesignation.NORMAL_USER]
#
#     @staticmethod
#     def get_is_channel(obj):
#         return obj.user_type == User.CHANNEL
#
#     @staticmethod
#     def get_designation(obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             return user_designation.eng_name
#         else:
#             return UserDesignation.NORMAL_USER
#
#     @staticmethod
#     def _get_district_display_name(address):
#         try:
#             district = address.village.block.district
#             state = district.state
#             return "%s, %s" % (district.name, state.name)
#         except:
#             return ""
#
#     @staticmethod
#     def _get_block_display_name(address):
#         try:
#             district = address.block.district
#             state = district.state
#             return "%s, %s" % (district.name, state.name)
#         except:
#             return ""
#
#     def get_description(self, obj):
#         _user_description = ""
#         if obj.designation and obj.designation in UserDesignation.SPECIAL_USERS:
#             _user_description = UserDesignation.display_name[obj.designation]
#         if not _user_description:
#             _user_description = self._get_district_display_name(obj.address)
#
#         if not _user_description:
#             try:
#                 _user_description = self._get_block_display_name(obj.derived_addresses)
#             except:
#                 pass
#
#         return _user_description
#
#     def _get_default_image(self):
#         default_image_qs = DefaultImage.objects.filter(image_type=base.ImageType.COVER).first()
#         if default_image_qs:
#             return UserCoverImageSerializer(default_image_qs, context=self.context).data
#         return None
#
#     def get_cover_image(self, obj):
#         image = None
#         if hasattr(obj, 'cover_image'):
#             image = UserCoverImageSerializer(obj.cover_image, context=self.context).data
#         elif hasattr(obj, 'user_designation'):
#             image = DesignationImageSerializer(obj.user_designation, context=self.context).data
#         if not image or not image.get('image'):
#             return self._get_default_image()
#         return image
#
#     def get_derived_address(self, obj):
#         derived_address_qs = DerivedAddress.objects.filter(~Q(block=None), user=obj).first()
#         if derived_address_qs:
#             return DerivedAddressSerializer(derived_address_qs, context=self.context).data
#         else:
#             return None
#
#     def validate_topic_ids(self, value):
#         if value:
#             return Topic.objects.filter(id__in=value).values_list('id', flat=True)
#         return value
#
#     def validate_crop_ids(self, value):
#         if value:
#             return Crop.objects.filter(id__in=value).values_list('id', flat=True)
#         return value
#
#     def validate_village_id(self, value):
#         if value:
#             try:
#                 return Village.objects.get(id=value)
#             except Village.DoesNotExist:
#                 raise serializers.ValidationError(_('Please chose correct village.'))
#         return value
#
#     def get_partner(self, value):
#         require_partner = self.context.get('require_partner', False)
#         if require_partner:
#             partner_data = get_partner(str(value.id))
#             if not partner_data and value.user_business_profile.first():
#                 partner_data = {}
#             return partner_data
#         return None
#
#     def get_user_designation(self, obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             choice = user_designation.designation_display_choice
#             if choice == DESIGNATION_DISPLAY_CHOICES_SHOW:
#                 return DesignationSerializer(user_designation).data
#         return None
#
#     def update(self, instance, validated_data):
#         village = validated_data.pop('village_id', None)
#         location_id = validated_data.pop('location_id', None)
#         location_type = validated_data.pop('location_type', None)
#         address_info = validated_data.pop('address_info', None)
#         view = self.context.get('view')
#         request = self.context.get('request')
#         point = view.get_filter_point(request)
#         if village is not None or address_info:
#             if instance.address:
#                 address = instance.address
#                 address.village = village if village else None
#                 address.location = point
#                 if location_id is not None and location_type is not None:
#                     address.location_id = location_id
#                     address.location_type = location_type
#                     address.extras = address_info if address_info else None
#
#                 address.save()
#             else:
#                 query = {}
#                 if location_id is not None and location_type is not None:
#                     query = {'location_id': location_id, 'location_type': location_type}
#                 if address_info:
#                     query.update({'extras': address_info})
#                 if village:
#                     query.update({'village': village})
#                 query.update({'location': point})
#                 address = Address.objects.create(
#                     **query
#                 )
#                 instance.address = address
#                 instance.save()
#
#         if instance.address:
#             try:
#                 derived_address = DerivedAddress.objects.get(user=instance, is_active=True)
#                 derived_address.is_active = False
#                 derived_address.save()
#
#             except DerivedAddress.DoesNotExist:
#                 pass
#
#         new_topic_ids = validated_data.pop('topic_ids', None)
#         entity_update_type_list = []
#         if new_topic_ids is not None:
#             new_topic_ids = set(new_topic_ids)
#             current_topic_ids = set(UserTopic.objects.filter(user=instance).values_list('topic_id', flat=True))
#
#             # Insert new topics first
#             to_be_added = list()
#             for topic_id in set(new_topic_ids - current_topic_ids):
#                 to_be_added.append(UserTopic(user=instance, topic_id=topic_id))
#             if to_be_added:
#                 UserTopic.objects.bulk_create(to_be_added)
#                 entity_update_type_list.append(UserStageName.Topic)
#
#             # Delete remove topics
#             UserTopic.objects.filter(user=instance, topic_id__in=list(current_topic_ids - new_topic_ids)).delete()
#
#         # Do Same for crops
#         new_crop_ids = validated_data.pop('crop_ids', None)
#         if new_crop_ids is not None:
#             new_crop_ids = set(new_crop_ids)
#             current_crop_ids = set(UserCrop.objects.filter(user=instance).values_list('crop_id', flat=True))
#
#             # Insert new crops first
#             to_be_added = list()
#             for crop_id in set(new_crop_ids - current_crop_ids):
#                 to_be_added.append(UserCrop(user=instance, crop_id=crop_id))
#             if to_be_added:
#                 UserCrop.objects.bulk_create(to_be_added)
#                 entity_update_type_list.append(UserStageName.Crop)
#
#             # Delete remove crops
#             UserCrop.objects.filter(user=instance, crop_id__in=list(current_crop_ids - new_crop_ids)).delete()
#         if entity_update_type_list:
#             publish(ps_topic.EntityFollow, user_id=str(instance.id), entity_update_type_list=entity_update_type_list)
#         return super().update(instance, validated_data)
#
#     def get_business_profile(self, obj):
#         require_business_profile = self.context.get('require_business_profile', False)
#         if require_business_profile:
#             business_profile = obj.user_business_profile.first()
#             if business_profile and business_profile.allow_business_page_creation:
#                 from ..business.serializers.profile_serializers import BasicBusinessProfileSerializer
#                 return BasicBusinessProfileSerializer(business_profile).data
#         return None
#
#     def get_location_name(self, obj):
#         request = self.context.get('request')
#         user_address = obj.address
#         location_name = ''
#         if user_address:
#             from ..users.services.user_services import get_user_location_name_wrt_village_or_address_meta_data
#             _, _, _, location_name = get_user_location_name_wrt_village_or_address_meta_data \
#                 (user_village_address=user_address.village, meta_data=None)
#         else:
#             (x, y) = Request(request).lat_lon
#             if x is None or y is None or default_location(x, y):
#                 return ''
#             try:
#                 lat, lon = float(x), float(y)
#                 _, _, location_name = LocationService().get_location_by_lat_lon(lat, lon)
#                 location_name = get_trimmed_location_name(location_name)
#             except:
#                 pass
#         return location_name if not is_empty_text(location_name) else ''
#
#
# class UserAuthSerializer(UserSerializer):
#     firebase_auth_token = serializers.SerializerMethodField()
#
#     def get_firebase_auth_token(self, obj):
#         try:
#             return auth.create_custom_token(str(obj.id))
#         except:
#             return ''
#
#     class Meta(UserSerializer.Meta):
#         fields = UserSerializer.Meta.fields + ['firebase_auth_token']
#
#
# class PhoneBookSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserPhoneBook
#         fields = ['user', 'phone_book']
#
#
# class UserRatingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserRating
#         fields = ['user', 'rating', "selected_options", "feedback", "not_interested"]
#
#
# class DerivedAddressSerializer(serializers.ModelSerializer):
#     block = BlockSerializer()
#     district = DistrictSerializer(source='block.district')
#     state = StateSerializer(source='block.district.state')
#     name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = DerivedAddress
#         fields = ['id', "location", "block", "district", 'state', 'name', "is_active"]
#
#     def get_name(self, obj):
#         display_address = None
#         if obj.block:
#             display_address = (obj.block.district.name
#                                + ", " + obj.block.district.state.name)
#         return display_address
#
#
# class DeviceRegistration(serializers.Serializer):
#     fcm_token = serializers.CharField(required=True)
#     lat = serializers.FloatField(required=True)
#     lon = serializers.FloatField(required=True)
#     device_id = serializers.CharField(required=False)
#     device_name = serializers.CharField(required=False)
#     device_type = serializers.CharField(required=False)
#     version_code = serializers.IntegerField(required=False)
#
#
# class EntityFollowSerializer(serializers.Serializer):
#     id = serializers.UUIDField(required=True)
#     type = serializers.CharField(required=True)
#     is_following = serializers.BooleanField(required=False)
#
#
# class UserFeedBaseSerializer(UserSerializer):
#     name = serializers.SerializerMethodField()
#     location_text = serializers.SerializerMethodField()
#
#     class Meta(UserSerializer.Meta):
#         fields = ['id', 'full_name', 'name', 'designation', 'image', 'address',
#                   "derived_address", "user_designation", "is_verified",
#                   "location_text"]
#
#     @staticmethod
#     def get_name(obj):
#         return obj.full_name
#
#     def get_location_text(self, obj):
#         location_text_required = self.context.get('location_text_required')
#         location_text = ''
#         if location_text_required:
#             location_text = self.context.get('location_text')
#             if location_text:
#                 return location_text
#             try:
#                 location_text = UserLocationService(user=obj).get_location_name()
#             except Exception as e:
#                 pass
#         return location_text
#
#
# class UserDetailSerializer(UserSerializer):
#     name = serializers.SerializerMethodField()
#     location_text = serializers.SerializerMethodField()
#     is_spammer = serializers.SerializerMethodField()
#     user_designation = serializers.SerializerMethodField()
#
#     class Meta(UserSerializer.Meta):
#         fields = ['id', 'full_name', 'name', 'is_phone_number_public', 'user_type', 'designation',
#                   'designation_display_name', 'bio', 'image', 'address', 'date_joined', 'onboarded_at', 'topics',
#                   'crops', 'topic_ids', 'crop_ids', 'village_id', "leader_count", "follower_count", "cover_image",
#                   "derived_address", "description", "user_designation", "is_verified", "partner", "is_channel",
#                   "location_text", "is_spammer"]
#
#     def get_user_designation(self, obj):
#         user_designation = obj.user_designation
#         if user_designation:
#             return DesignationSerializer(user_designation).data
#         return None
#
#     @staticmethod
#     def get_is_spammer(obj):
#         user_spammer = UserSpammerInfo.objects.filter(user=obj, is_active=True).exists()
#         return user_spammer
#
#     @staticmethod
#     def get_name(obj):
#         return obj.full_name
#
#     def get_location_text(self, obj):
#         location_text_required = self.context.get('location_text_required')
#         location_text = ''
#         if location_text_required:
#             location_text = self.context.get('location_text')
#             if location_text:
#                 return location_text
#             try:
#                 location_text = UserLocationService(user=obj).get_location_name()
#             except Exception as e:
#                 pass
#         return location_text
#
#
# class UserRatingMarkSerializer(serializers.Serializer):
#     user_id = serializers.UUIDField()
#     rating_by = serializers.UUIDField()
#     rating = serializers.IntegerField()
#
#
# class UserProfessionSerializer(serializers.ModelSerializer):
#     image = NullableVersatileImageFieldSerializer(sizes='content_image')
#     selected_image = NullableVersatileImageFieldSerializer(sizes='content_image')
#     is_selected = serializers.SerializerMethodField()
#
#     class Meta:
#         model = UserProfession
#         fields = ('id', 'display_text', 'order', 'is_active', 'image', 'selected_image', 'is_selected')
#
#     def get_is_selected(self, obj):
#         user = self.context.get('user')
#         qs = UserProfessionMapping.objects.filter(user=user, profession=obj, is_active=True)
#         if qs:
#             return True
#         return False
#
#
# class UserProfessionUpdateSerializer(serializers.Serializer):
#     profession_id = UUIDListField()
#
#
# class UserIsVerifiedMarkSerializer(serializers.Serializer):
#     user_id = serializers.UUIDField()
#     is_verified = serializers.BooleanField()
#     is_active = serializers.BooleanField(default=True)
