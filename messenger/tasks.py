import os

from django.core.files.base import ContentFile

from celery import shared_task
from celery.decorators import task
from celery.utils.log import get_task_logger

import time
from django.core.management import call_command
# from messenger.serializers import FilePatchSerializer, FileSerializer
from messenger.models import ChatData

logger = get_task_logger(__name__)

# @task(name="save_message_db", bind=True)
@task(name="save_message_db")
def save_message_db(pk=None):
    time.sleep(1)
    obj = ChatData.objects.get(id=pk)
    #
    # logger.error(f'arg pk: {pk}')
    # logger.error(f'object pk: {obj.id}')
    obj.update_file_from_cache()

    return 'task done'

    # return serializer

# @task(name="update_file")
# def save_message_db():
#     serializer = FileSerializer
#
#     return serializer