from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from messenger.models import ChatData, Crypt, CustomUser
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.utils.functional import cached_property

from messenger.serializers import ChatCreateSerializer, ChatPartialUpdateSerializer, ChatDataSerializer, \
    ChatDataDetailSerializer, CustomUserSerializer

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from messenger.permisions import IsOwner
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from messenger.tasks import save_message_db
from rest_framework import serializers
import time
from silk.profiling.profiler import silk_profile
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache

# Create your views here.

class PingViewSet(GenericViewSet, ListModelMixin):
    """
    Helpful class for internal health checks
    for when your server deploys. Typical of AWS
    applications behind ALB which does default 30
    second ping/health checks.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        return Response(
            data={"id": request.GET.get("id")},
            status=status.HTTP_200_OK
        )

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            cache.clear()
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomUserSetView(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['get']

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={201: CustomUserSerializer}, )
    @never_cache
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], name='me')
    @never_cache
    def me(self, request, pk=None, **kwargs):
        self_user = self.request.user
        serializer = self.get_serializer(self_user, many=False)

        return Response(serializer.data)

class ChatDataSetView(ModelViewSet):
    queryset = ChatData.objects.all().order_by('-updated').select_related('crypto').prefetch_related('owner')
    # queryset = ChatData.objects.none()
    serializer_class = ChatDataSerializer
    # http_method_names = ['get', 'post', 'patch', 'delete']

    # lookup_field = "pk"

    # permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     return self.request.user.profile.chatdata_set.all()

    def get_queryset(self):
        self_user = self.request.user
        qs = self_user.chatdata_set.all()

        # qs = ChatData.objects.filter(owner__contains=self_id)

        return qs

    def get_permissions(self):
        permission_classes = [IsOwner, IsAuthenticated, IsAdminUser]
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action == 'list':
            permission_classes = [IsOwner]
        elif self.action == 'retrieve':
            permission_classes = [IsOwner]
        elif self.action == 'partial_update':
            permission_classes = [IsOwner]
        elif self.action == 'destroy' or self.action == 'update':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def validate_message_len(self, message):
        if len(message) > 3750:
            raise serializers.ValidationError(
                "Ensure this field has no more than 3750 characters. It is A4 size Word document with text in the Arial font (font size 12, not bold)")
        return message

    @extend_schema(request=ChatCreateSerializer, responses={201: ChatDataSerializer}, )
    def create(self, request, *args, **kwargs):
        users_code_string = request.data["owner"]
        users_code = users_code_string.split(', ')
        self_uuid = str(request.user.id)
        users_code.append(self_uuid)
        new_chat = ChatData.objects.create_chat(users_code)
        serializer = self.get_serializer(new_chat, many=False)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # @silk_profile(name='Chat list')
    @method_decorator(cache_page(0))
    @extend_schema(responses={201: ChatDataSerializer}, )
    @never_cache
    def list(self, request, *args, **kwargs):
        self_user = request.user

        # queryset = ChatData.objects.all().order_by('-updated').prefetch_related('owner')
        #
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @silk_profile(name='Chat retrieve')
    @method_decorator(cache_page(0))
    @extend_schema(parameters=[
        OpenApiParameter("pk", OpenApiTypes.UUID, OpenApiParameter.QUERY),
    ], responses={201: ChatDataDetailSerializer}, )
    def retrieve(self, request, pk=None, **kwargs):
        pk_str = str(pk)
        # obj = self.get_object(pk)
        # self_profile = self.request.user.profile

        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=pk_str)

        serializer = ChatDataDetailSerializer(obj, many=False)

        return Response(serializer.data)

    @method_decorator(cache_page(0))
    @extend_schema(parameters=[
        OpenApiParameter("pk", OpenApiTypes.UUID, OpenApiParameter.QUERY),
    ], request=ChatPartialUpdateSerializer, responses={201: ChatDataDetailSerializer}, )
    def partial_update(self, request, pk=None, **kwargs):
        # time.sleep(1)
        pk_str = str(pk)
        # obj = self.get_object(pk)
        self_uuid = self.request.user
        # self_user_code = self_profile.code

        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=pk_str)
        raw_message = request.data["new_message"]
        new_message = self.validate_message_len(raw_message)

        obj.cache_update = obj.add_message(new_message, str(self_uuid))
        TASK_COUNTDOWN_s = 20
        save_message_db.apply_async((pk_str,), countdown=TASK_COUNTDOWN_s, task_id=pk_str)

        serializer = ChatDataDetailSerializer(obj, many=False)

        return Response(serializer.data)

    @silk_profile(name='Chat destroy')
    @extend_schema(parameters=[
        OpenApiParameter("pk", OpenApiTypes.UUID, OpenApiParameter.QUERY),
    ], responses={204: None}, )
    def destroy(self, request, pk=None, **kwargs):
        pk_str = str(pk)
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=pk_str)
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendsSetView(ModelViewSet):
    # queryset = CustomUser.objects.all().prefetch_related('friends')
    # queryset = ChatData.objects.none()
    serializer_class = CustomUserSerializer
    # http_method_names = ['post', 'list', 'retrieve', 'delete']
    http_method_names = ['post', 'get']
    def get_queryset(self):
        queryset = self.request.user.friends.all()
        # queryset = self.queryset
        # if isinstance(queryset, CustomUser):
        #     # Ensure queryset is re-evaluated on each request.
        #     queryset = queryset.all()
        return queryset

    @silk_profile(name='Friends list')
    @method_decorator(cache_page(0))
    @extend_schema(responses={201: CustomUserSerializer}, )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @silk_profile(name='Friends create')

    # @action(detail=False, methods=['post'])
    @extend_schema(request=ChatCreateSerializer, responses={201: CustomUserSerializer}, )
    def create(self, request, *args, **kwargs):
        obj = request.user
        friend_uuid = request.data["users_uuid"]
        all_friends = obj.add_friend(friend_uuid)

        serializer = self.get_serializer(all_friends, many=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

