import os
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

FILE_ROOT = os.path.join(settings.BASE_DIR, 'message_storage')
FILE_URL = "/messages/"


@deconstructible
class MessagesSystemStorage(FileSystemStorage):
    def __init__(self, subdir):
        self.subdir = subdir
        super(MessagesSystemStorage, self).__init__(location=os.path.join(FILE_ROOT, self.subdir),
                                                    base_url=urljoin(FILE_URL, self.subdir)),

    def __eq__(self, other):
        return self.subdir == other.subdir

    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(FILE_ROOT, name))
        return name
