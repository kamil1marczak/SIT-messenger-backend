from django.urls import path, include, re_path

from messenger.views import PingViewSet, ChatDataSetView, FriendsSetView, LogoutView, CustomUserSetView

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )

from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter, DefaultRouter
# from drf_auto_endpoint.router import router
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# #ping router for vue js
router_ping = DefaultRouter()
router_ping.register('ping', PingViewSet, basename="ping")

router = SimpleRouter()
# router.register(r'v1', ChatSetView, basename='v1')
router.register(r'chat', ChatDataSetView, basename='chat')
router.register(r'friends', FriendsSetView, basename='friends')
router.register(r'users', CustomUserSetView, basename='users')

urlpatterns = [

    path('v1/', include(router.urls)),
    path('v1/', include(router_ping.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/jwt/logout/', LogoutView.as_view(), name='auth_logout'),
    path('silk/', include('silk.urls', namespace='silk')),

    # YOUR PATTERNS
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # path('openapi', get_schema_view(
    #     title="Meanger-re",
    #     description="API for all things …",
    #     version="1.0.0"
    # ), name='openapi-schema'),
    # Optional UI:
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # path('swagger-ui/', TemplateView.as_view(
    #     template_name='swagger-ui.html',
    #     extra_context={'schema_url': 'openapi-schema'}
    # ), name='swagger-ui')

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
