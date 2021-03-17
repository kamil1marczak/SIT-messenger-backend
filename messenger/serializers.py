import os
from datetime import datetime

import pytz
from django.contrib.auth.models import User, Group
from django.db.models import Q

from messenger.models import ChatData, CustomUser
from rest_framework import serializers




# response serializers for Open Api
class ChatCreateSerializer(serializers.Serializer):
    users_code = serializers.ListField(child=serializers.UUIDField(format='hex_verbose'))


class ChatPartialUpdateSerializer(serializers.Serializer):
    new_message = serializers.CharField(max_length=3750)

#Model Set View
class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username']

class ChatDataSerializer(serializers.ModelSerializer):
    # owner = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    # owner = serializers.CurrentUserDefault()
    # owner = CustomUserSerializer(many=True, read_only=True)

    class Meta:
        model = ChatData
        fields = ['id', 'created', 'updated', 'owner']
        # read_only_fields = ['owner']
        #
        # extra_kwargs = {
        #     'users': {'read_only': True}
        # }



class ChatDataDetailSerializer(serializers.ModelSerializer):
    # users_code = serializers.CharField(source='users_name')

    # owner = serializers.CurrentUserDefault()
    owner = CustomUserSerializer(many=True, read_only=True)

    message_data = serializers.DictField()
    cache_messages = serializers.DictField()

    class Meta:
        model = ChatData
        fields = ['id', 'created', 'updated', 'owner', 'message_data', 'cache_messages']
        read_only_fields = ['id', 'created', 'updated']
