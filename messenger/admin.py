from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
# from django.contrib.admin.views.main import ChangeList
# from django import forms
#
# from django.urls import path
# from django.http import JsonResponse
# # from django.views.decorators.csrf import csrf_exempt

# Register your models here.
from messenger.models import ChatData, Crypt, CustomUser


class ChatDataAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super(ChatDataAdmin, self).get_queryset(request).prefetch_related('owner')
        return queryset

    def show_usernames(self, obj):
        return "\n".join([elem.username for elem in obj.owner.all()])


    readonly_fields = ['id', 'created', 'updated', 'owner', 'message_data', 'message_file']
    fields = []

    list_display = ['id', 'created', 'updated', 'show_usernames']
    ordering = ['-created']
    search_fields = ['owner']
    # list_filter = ['users_name']
    list_filter = (
        ('owner', admin.RelatedOnlyFieldListFilter),
    )



class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
    list_display = ('id', 'username', 'email', 'is_staff', 'is_active',)
    list_filter = ('id', 'username', 'email', 'is_staff', 'is_active',)

    search_fields = ('id',)
    ordering = ('username',)


class CryptAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super(CryptAdmin, self).get_queryset(request)
        return queryset

    readonly_fields = ['id']
    fields = ['code', 'key']

    list_display = ['id', 'code', 'key']
    # list_filter = ['users_name']


admin.site.register(ChatData, ChatDataAdmin)
# admin.site.register(Profile, ProfileDataAdmin)
admin.site.register(Crypt, CryptAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
