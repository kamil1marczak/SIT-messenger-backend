import os
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import pytz
import uuid

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.cache import cache
from messenger.utils import get_bytes, generate_password_key
from cryptography.fernet import Fernet

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
        users = CustomUser.objects.filter(id__in=users_code)
        now = datetime.now(pytz.utc)
        message = dict(datetime=now.isoformat(), user="", message="Beginning of messages")
        message_data = dict(messages=[message, ])
        crypto_tool = Crypt.objects.create_crypto()
        message_data_encrypted = crypto_tool.encrypt(str(message_data))
        message_file = ContentFile(message_data_encrypted)
        message_file.name = '-AND-'.join([str(elem) for elem in users]) + '.txt'
        chat = ChatData(message_file=message_file, crypto=crypto_tool)
        chat.save()
        chat.owner.set(users)
        return chat

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related('crypto')

class ChatData(OwnedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    message_file = models.FileField(storage=FileSystemStorage(location=settings.MEDIA_ROOT),
                                    upload_to='message_storage')
    crypto = models.ForeignKey(Crypt, on_delete=models.CASCADE)
    objects = ChatDataManager()

    class Meta:
        ordering = ['-updated']

    @property
    def message_data(self):
        encrypted_messages = self.message_file.read()
        self.message_file.seek(0)
        message_dict = eval(self.crypto.decrypt(encrypted_messages))
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
        cache.delete(f'messages.{id}')
        cache.set(f'messages.{id}', messages, timeout=None)

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
        logger.error(f'cache message: {str(messages_concat)}')

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

    def __str__(self):
        return str(self.id)
