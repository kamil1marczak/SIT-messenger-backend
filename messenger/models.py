import itertools
import os

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.db.models import Count, Q
from datetime import datetime, timedelta
import pytz
import uuid

from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext as _
import json
from django.core.cache import cache
# Third-party
from django.views.decorators.cache import never_cache

# from messenger.crypt import Cryptographer
# from messenger.storage import MessagesSystemStorage, FILE_ROOT
from messenger.utils import get_bytes, generate_password_key

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import logging

logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    pass
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    friends = models.ManyToManyField("self", blank=True)

    def add_friend(self, users_code_string):
        users_code = users_code_string.split(', ')
        users = CustomUser.objects.filter(id__in=users_code)
        self.friends.set(users)
        return self.friends.all()

    def __str__(self):
        # return str(self.id)
        return str(self.username)


class OwnedModel(models.Model):
    owner = models.ManyToManyField(settings.AUTH_USER_MODEL)

    class Meta:
        abstract = True

class CryptManager(models.Manager):
    def create_crypto(self, password=None):
        if password:
            key = generate_password_key(password=password)
            is_chat_password = True
        else:
            key = Fernet.generate_key()
            is_chat_password = False
        crypt = self.create(key=key, is_chat_password=is_chat_password)
        return crypt

class Crypt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='crypto_id', unique=True)
    code = models.UUIDField(default=uuid.uuid4)
    is_chat_password = models.BooleanField(default=False)
    key = models.BinaryField(null=True)

    objects = CryptManager()

    @property
    def chat_password(self):
        return None
    #
    # @chat_password.setter
    # def user_password(self, password):
    #


    @property
    def fernet(self):
        if self.is_chat_password:
            key = generate_password_key(self.chat_password)
            return Fernet(key)
        return Fernet(self.key)

    def encrypt(self, message):
        b_message = get_bytes(message)
        # encrypted_message = self.fernet.encrypt(b_message)
        encrypted_message = self.fernet.encrypt(b_message)
        return encrypted_message

    def decrypt(self, encrypted_message):
        b_message = get_bytes(encrypted_message)
        # decrypted_message = self.fernet.decrypt(b_message)
        decrypted_message = self.fernet.decrypt(b_message)
        return decrypted_message


    def __str__(self):
        return str(self.id)


class ChatDataManager(models.Manager):

    def create_chat(self, users_code):
        password_code = uuid.uuid4()
        # users_code = users_code_string.split(', ')
        # users = Profile.objects.filter(code__in=users_code)
        users = CustomUser.objects.filter(id__in=users_code)
        now = datetime.now(pytz.utc)
        message = dict(datetime=now.isoformat(), user="", message="Beginning of messages")
        message_data = dict(messages=[message, ])
        crypto_tool = Crypt.objects.create_crypto()
        # crypto_tool.save()

        # crypto_tool = Cryptographer(password_code.bytes)
        message_data_encrypted = crypto_tool.encrypt(str(message_data))

        message_file = ContentFile(message_data_encrypted)
        message_file.name = '-AND-'.join([str(elem) for elem in users]) + '.txt'
        # crypto = Crypt(code=password_code)
        # crypto.save()
        chat = ChatData(message_file=message_file, crypto=crypto_tool)
        chat.save()
        chat.owner.set(users)

        return chat

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('crypto')

class ChatData(OwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # code = models.UUIDField(default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # users = models.ManyToManyField(User)
    # message_file = models.FileField(upload_to='message_storage')
    message_file = models.FileField(storage=FileSystemStorage(location=settings.MEDIA_ROOT),
                                    upload_to='message_storage')
    crypto = models.ForeignKey(Crypt, on_delete=models.CASCADE)

    # message_file = models.FileField(storage=MessagesSystemStorage('storage'))
    # message_file = models.FileField(upload_to='storage')

    objects = ChatDataManager()

    class Meta:
        ordering = ['-updated']
        # constraints = [
        #     models.UniqueConstraint(fields=['app_uuid', 'version_code'], name='unique appversion')
        # ]

    # @property
    # def users_name(self):


    @property
    def message_data(self):
        encrypted_messages = self.message_file.read()
        self.message_file.seek(0)
        message_dict = eval(self.crypto.decrypt(encrypted_messages))
        # message_dict = json.loads(self.crypto_tool.decrypt(self.message_file.read())) if self.message_file else dict
        if message_dict is None:
            message_dict = dict()
            message_dict['messages'] = list()
        return message_dict

    def add_message(self, new_message_str, user=""):
        id = self.id

        messages = dict(messages=list())

        if f'messages.{id}' in cache:
            messages = cache.get(f'messages.{id}')

        now = datetime.now(pytz.utc)
        message = dict(datetime=now.isoformat(), user=user, message=new_message_str)
        messages['messages'].append(message)
        # messages[str(now)] = new_message_str
        # new_messages = messages.update(new_message_str)
        cache.delete(f'messages.{id}')
        cache.set(f'messages.{id}', messages, timeout=None)

        # logger.error(f'message add : {str(messages)}')

        return now

    @property
    def cache_messages(self):
        id = self.id

        if f'messages.{id}' in cache:
            messages = cache.get(f'messages.{id}')
        else:
            messages = dict(messages=list())

        return messages

    def update_file_from_cache(self):
        id = self.id

        messages_db = self.message_data
        cache_messages = cache.get(f'messages.{id}')

        messages_concat = messages_db['messages'] + cache_messages['messages']
        message_data = dict(messages=messages_concat)

        # logger.error(f'messages : {str(messages)}')

        logger.error(f'cache message: {str(messages_concat)}')
        # logger.error(f'id : {str(id)}')

        messages_encrypted = self.crypto.encrypt(str(message_data))
        old_filename = self.message_file.name
        # old_name = os.path.split(old_filename)
        old_name = os.path.split(old_filename)
        message_file = ContentFile(messages_encrypted)
        message_file.name = old_name[1]
        self.message_file.delete()

        self.message_file = message_file
        self.save(update_fields=['message_file'])
        cache.delete(f'messages.{id}')

    # @cached_property
    # def users_name(self):
    #     users = self.user.select_related('user').all()
    #     users_string = ', '.join([str(elem.user) for elem in users])
    #
    #     return users_string

    def __str__(self):
        return str(self.id)

# @receiver(post_save, sender=ChatData)
# def create_chat_code(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=ChatData)
# def save_chat_code(sender, instance, **kwargs):
#     instance.profile.save()


# class OwnedModel(models.Model):
#     owner = models.ForeignKey(settings.AUTH_USER_MODEL,
#     on_delete=models.CASCADE)
#
#     class Meta:
#         abstract = True
#
# class Belonging(OwnedModel):
#     name = models.CharField(max_length=100)
