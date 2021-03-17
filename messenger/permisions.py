from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    message = "Access denied."

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner

# class IsOwnerOrReadOnly(permissions.BasePermission):
#     #permision require for all cases to be authentificated!
#
#     message = "Access denied."
#
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return request.user in obj.users
