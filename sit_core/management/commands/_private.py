from messenger.models import CustomUser
from django.contrib.auth.hashers import make_password


def populate_user():
    user_list = [
        ['root', 'root@root.com', True, True],
        ['Marlena', 'marlena@marlena.com', False, False],
        ['Karol', 'karol@karol.com', False, False],
        ['Zbigniew', 'zbigniew@zbigniew.com', False, False],
        ['Natalia', 'natalia@natalia.com', False, False],
    ]

    CustomUser.objects.bulk_create([
        CustomUser(
            username=user[0],
            email=user[1],
            is_staff=user[2],
            is_superuser=user[3],
            is_active=True,
            password=make_password('Kamil100!'),
        ) for user in user_list
    ])
