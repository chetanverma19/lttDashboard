# -*- coding: utf-8 -*-
from cache_memoize import cache_memoize
from celery import shared_task
from rest_framework import permissions, viewsets, decorators
from farmstock import feed, fa_logger
# farmstock Modules
from farmstock.app_config.models import AppVariable, CeleryTest, FirebaseCollection, BottomNavigation, TimezoneDetail, \
    DEFAULT_TIMEZONE, BOTTOM_NAV_TYPE_DISCOURSE, AppDrawerSection, KubePodConfig
from farmstock.base import models as base_model, serializers as base_serializer, exceptions
from farmstock.base import response
from django.contrib.gis.geos import Point
from farmstock.base.models import Topic
from farmstock.feed.algorithms.feed_algorithm_first_session.services import can_show_first_session_feed
from farmstock.feed.services.feed_manager import FeedManager
from farmstock.marketplace.models.registration import MarketplaceUser
from farmstock.user_network import service as referral_service
from farmstock.util import get_version_code, get_celery_task_count
from .serializers import AppConfigSerializer, FirebaseCollectionSerializer, BottomNavigationSerializer, \
    TimezoneDetailSerializer, AppDrawerSerializer, AndroidApkSerializer
from farmstock.weather.services import get_today_weather_data
from ..alert.send_alert import send_android_apk_push_alert
import redis


@cache_memoize(60 * 5)
def _get_staff_filter():
    user_filter = []
    user_filter.append({"type": feed.FILTER_TYPE_FEED_ALGORITHM_FIRST_SESSION, "name": "First Session",
                        "has_follow_button": True, "has_time": True})
    user_filter.append({"type": feed.FILTER_TYPE_NO_FILTER, "name": "सारे",
                        "has_follow_button": True, "has_time": False})

    user_filter.append({"type": feed.FILTER_TYPE_UNANSWERED, "name": "NAns",
                        "has_follow_button": True, "has_time": True})
    user_filter.append({"type": feed.FILTER_TYPE_UNANSWERED_1DAY_AGO, "name": " NAns1",
                        "has_follow_button": True, "has_time": True})
    user_filter.append({"type": feed.FILTER_TYPE_1DAY_AGO, "name": "1 days ago",
                        "has_follow_button": True, "has_time": True})
    user_filter.append({"type": feed.FILTER_TYPE_2DAY_AGO, "name": "2 days ago",
                        "has_follow_button": True, "has_time": True})
    user_filter.append({"type": feed.FILTER_TYPE_5DAY_AGO, "name": "5 days ago",
                        "has_follow_button": True, "has_time": True})
    user_filter.append({"type": feed.FILTER_TYPE_7DAY_AGO, "name": "7 days ago",
                        "has_follow_button": True, "has_time": True})
    return user_filter


class AppConfigCheckViewSet(viewsets.GenericViewSet):
    """
    create:
    Check app configuration from server
    """
    point_param = 'point'
    serializer_class = AppConfigSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return None

    def create(self, request, *args, **kwargs):
        context = {'request': request}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        update_result = serializer.get_update_result()
        helpline_number = AppVariable.objects.get_helpline_number()
        data = {
            'update': update_result,
            'helpline_number': helpline_number
        }
        return response.Ok(data=data)

    def get_organic_farming_type(self):
        pass

    def get_buy_sell_tab(self):
        topic = Topic.objects.filter(eng_title='buy-sell').first()
        if topic is not None:
            return {"type": feed.FILTER_TYPE_TOPIC_POST + feed.FILTER_SEPARATOR + str(topic.id), "name": topic.title}
        return None

    @staticmethod
    def _get_firebase_collection():
        qs = FirebaseCollection.objects.filter(is_active=True)
        data = {}
        for coll in FirebaseCollectionSerializer(qs, many=True).data:
            data[coll['key']] = coll['name']
        return data

    def _get_user_specific_feed_filter(self, user):
        user_filter = []
        if user.is_anonymous:
            return user_filter
        if user.is_staff:
            user_filter.extend(_get_staff_filter())

        for crop in user.crops.all()[:1]:
            _id, name = crop.id, crop.title
            user_filter.append({"type": feed.FILTER_TYPE_CROP_POST + feed.FILTER_SEPARATOR + str(_id), "name": name})
        for topic in user.topics.all()[:1]:
            _id, name = topic.id, topic.title
            user_filter.append({"type": feed.FILTER_TYPE_TOPIC_POST + feed.FILTER_SEPARATOR + str(_id), "name": name})

        return user_filter

    @staticmethod
    def _get_header_widget():
        header_widget = [{"type": "today_tips"},
                         {"type": "widget_list",
                          "widgets": [{"type": "weather"}, {"type": "referral"}]
                          }]
        return header_widget

    def get_filter_point(self, request):
        point_string = request.query_params.get(self.point_param, None)
        if not point_string:
            return None
        try:
            (x, y) = (float(n) for n in point_string.split(','))
        except ValueError:
            raise exceptions.ParseError('Invalid geometry string supplied for parameter {0}'.format(self.point_param))

        p = Point(x, y)
        return p

    def _get_feed_filters(self, user):
        need_api_optimization = AppVariable.objects.need_api_optimization()

        for_user_post = {"header_widget": self._get_header_widget(), "type": feed.FILTER_TYPE_POST,
                         "name": "आपका नेटवर्क", "has_time": True, "has_follow_button": True}

        first_session_user_post = {"header_widget": self._get_header_widget(),
                                   "type": feed.FILTER_TYPE_FEED_ALGORITHM_FIRST_SESSION,
                                   "name": "आपका नेटवर्क", "has_time": False, "has_follow_button": True}

        krishify_post = {"type": feed.FILTER_TYPE_KRISHIFY_POST, "name": "Krishify ज्ञान", "has_follow_button": True,
                         "has_time": True}
        sawaal_jawaab = {"type": feed.FILTER_TYPE_FEED_QUESTION, "name": "सवाल जवाब", "is_post_type_question": True,
                         "has_time": True, "has_follow_button": True}
        infographic_post = {"type": feed.FILTER_TYPE_KRISHIFY_INFOGRAPHIC, "name": "इन्फोग्राफिक",
                            "has_follow_button": True, "has_time": True},
        video_post = {"type": feed.FILTER_TYPE_KRISHIFY_VIDEO, "name": "वीडियो", "has_follow_button": True,
                      "has_time": True}
        buy_sell_post = {"type": feed.FILTER_TYPE_BUY_SELL_POST, "name": "खरीद-बिक्री", "has_follow_button": True,
                         "has_time": True}

        if need_api_optimization:
            filters = [for_user_post, krishify_post, buy_sell_post, sawaal_jawaab]
        elif can_show_first_session_feed(user):
            filters = [first_session_user_post, buy_sell_post, krishify_post, sawaal_jawaab]
        else:
            filters = [for_user_post, krishify_post, buy_sell_post, sawaal_jawaab]

        filters.extend(self._get_user_specific_feed_filter(user))
        # buy_sell_tab = self.get_buy_sell_tab()
        # if buy_sell_tab:
        #     filters.append(buy_sell_tab)

        return filters

    def _replace_market_navigation_if_not_in_range(self, user, bottom_nav_option, request, market_fulfilment_radius):
        point = self.get_filter_point(request)
        can_replace = user.is_anonymous  # or not is_partner_in_area(point, market_fulfilment_radius)
        if can_replace:
            qs = BottomNavigation.objects.filter(type=BOTTOM_NAV_TYPE_DISCOURSE).first()
            return BottomNavigationSerializer(qs).data
        return bottom_nav_option

    def _get_dynamic_navigation_options(self, request, market_fulfilment_radius):
        user = request.user
        app_version = get_version_code(request)
        if not app_version:
            app_version = 0
        qs = BottomNavigation.objects.filter(is_active=True, version_start_cutoff__lte=app_version,
                                             version_end_cutoff__gt=app_version).order_by('order')

        new_nav_options = BottomNavigationSerializer(qs, many=True).data
        nav_options_list = []
        for option in new_nav_options:
            if option['type'] == "feed":
                option["tabs"] = self._get_feed_filters(user)

            # nois_login_required need to replace, as there will be global shops, so always visible
            # if option['type'] == BOTTOM_NAV_TYPE_KRISHI_BAZAAR:
            #     option = self._replace_market_navigation_if_not_in_range(user, option, request, market_fulfilment_radius)

            if option['type'] == "discourse":
                option["tabs"] = [
                    {"type": feed.FILTER_TYPE_DISCOURSE_QUESTION, "name": "सारे सवाल", "is_post_type_question": True},
                    {"type": feed.FILTER_TYPE_SELF_QUESTION, "name": "आपके सवाल",
                     "is_require_authentication": True,
                     "login_button_text": "लॉगिन करे",
                     "login_reason": "अपने पूछें हुए सवाल देखने के लिए लॉगिन करें",
                     "create_post_button": "सवाल पूछें", "create_post_reason": "आपने एक भी सवाल नहीं पुछा है"},
                ]
            nav_options_list.append(option)

        return nav_options_list

    def _get_weather_data(self, request):
        location = self.get_filter_point(request)
        if location is None:
            return {}
        latitude = round(location.y, 1)
        longitude = round(location.x, 1)
        weather_data = get_today_weather_data(latitude, longitude)
        return weather_data

    def get(self, request, *args, **kwargs):
        market_fulfilment_radius = AppVariable.objects.get_market_fulfillment_radius()
        user = request.user
        user_id = None
        if not user.is_anonymous:
            user_id = str(user.id)
        user = request.user
        is_marketplace_enabled = False
        can_show_phone_number = AppVariable.objects.can_show_phone_number(user_id)
        can_mask_call_banner_phone_number = AppVariable.objects.can_mask_post_banner_call_number()
        is_user_registered_in_marketplace = False
        is_feed_creation_enabled = False
        if not user.is_anonymous:
            mk_user = MarketplaceUser.objects.filter(user=user).first()
            if mk_user and mk_user.is_active:
                is_marketplace_enabled = True
                is_user_registered_in_marketplace = mk_user.is_registered
            # feed_creation_permission = FeedCreationPermission.objects.filter(user=user).first()
            # if feed_creation_permission and feed_creation_permission.is_active:
            #     is_feed_creation_enabled = True

        rating_queryset = base_model.Rating.objects.all()
        rating_serializer = base_serializer.RatingSerializer(rating_queryset, many=True)
        referral_link = None
        response_dict = dict(is_marketplace_enabled=is_marketplace_enabled,
                             can_show_phone_number=can_show_phone_number,
                             is_feed_creation_enabled=is_feed_creation_enabled,
                             is_user_registered_in_marketplace=is_user_registered_in_marketplace,
                             rating_data=rating_serializer.data, referral_link=referral_link,
                             dynamic_navigation_option=self._get_dynamic_navigation_options(
                                 request, market_fulfilment_radius),
                             firebase_collections=self._get_firebase_collection(),
                             market_fulfilment_radius=market_fulfilment_radius,
                             weather_data={},
                             # weather_data=self._get_weather_data(request),
                             enable_call_masking_on_banner=can_mask_call_banner_phone_number
                             )
        if not user.is_anonymous:
            response_dict['referral_link'] = referral_service.get_referral_link(user)
        return response.Response(response_dict)

    @decorators.action(detail=False, methods=['get'])
    def drawer(self, request, *args, **kwargs):
        qs = AppDrawerSection.objects.filter(is_active=True).all().order_by('order')
        data = AppDrawerSerializer(qs, many=True).data
        return response.Ok(data=data)

    @decorators.action(detail=False, methods=['post'], url_path='update_app_variable')
    def update_app_variable_key(self, request, *args, **kwargs):
        request_data = request.data
        name = request_data.get("name")
        detailed_value = request_data.get("detailed_value")
        value = request_data.get("value")
        AppVariable.objects.update_or_create(name=name, defaults={**dict(
            display_name=name, description=name, value=value, detailed_value=detailed_value
        )})
        return response.Ok()


@cache_memoize(1 * 60)
def _get_timezone(timezone):
    tz = TimezoneDetail.objects.filter(timezone=timezone).first()
    if tz is not None:
        serializer = TimezoneDetailSerializer(tz)
        return serializer.data
    elif timezone != DEFAULT_TIMEZONE:
        return _get_timezone(DEFAULT_TIMEZONE)
    else:
        return dict(timezone='Asia/Kolkata', locale='hi', login_method='otp')


class TimezoneDetailViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    @decorators.action(detail=False, methods=['get'])
    def info(self, request, *args, **kwargs):
        timezone = request.GET.get('timezone')
        return response.Response(data=_get_timezone(timezone))


@shared_task(bind=True, max_retries=3)
def celery_test_task(self, id):
    celery_test_obj = CeleryTest.objects.filter(id=id).first()
    fa_logger.debug("celery test id is {}".format(id))
    if celery_test_obj:
        celery_test_obj.task_completed = True
        celery_test_obj.save()


class CeleryTestViewSet(viewsets.GenericViewSet):

    @decorators.action(detail=False, methods=['get'])
    def task(self, request, *args, **kwargs):
        task = request.GET.get('id')
        celery_test = CeleryTest(task=task)
        celery_test.save()
        celery_test_task.delay(celery_test.id)
        return response.Ok()

    @decorators.action(detail=False, methods=['get'], url_path='task/count')
    def task_count(self, request, *args, **kwargs):
        task_count_map = get_celery_task_count()
        return response.Ok(data=task_count_map)


class KubePodConfigViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    @decorators.action(detail=False, methods=['get'])
    def config(self, request, *args, **kwargs):
        from django.utils import timezone
        curr_time = timezone.now().time()
        pod_config: KubePodConfig = KubePodConfig.objects.filter(start_at__lte=curr_time, end_at__gt=curr_time,
                                                                 is_active=True).first()
        if pod_config:
            return response.Ok(data={'min_number_of_pod': pod_config.min_number_of_pod})

        return response.NotFound()


class AndroidApkViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AndroidApkSerializer

    @decorators.action(detail=False, methods=['post'])
    def register(self, request, *args, **kwargs):
        data = self.serializer_class(data=request.data)
        data.is_valid(raise_exception=True)
        data.save()
        apk_path = data.validated_data.get('apk_path')
        commit_id = data.validated_data.get('commit_id')
        release_type = data.validated_data.get('release_type')
        flavor = data.validated_data.get('flavor')
        send_android_apk_push_alert(apk_path, commit_id, release_type, flavor)
        return response.Ok()
