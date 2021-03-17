from django.core.management.base import BaseCommand
from ._private import populate_user


class Command(BaseCommand):
    help = 'admin deployment'

    def handle(self, *args, **options):
        populate_user()
        self.stdout.write(self.style.SUCCESS("Succesfully populated table with users"))