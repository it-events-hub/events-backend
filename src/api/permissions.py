from rest_framework import permissions


class IsAuthorOrCreateOnly(permissions.BasePermission):
    """
    Allows anyone to create an application, allows only authenticated users
    to delete their own applications.
    """

    def has_permission(self, request, view):
        if view.action in ["create", "destroy"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if view.action == "destroy":
            return request.user.is_authenticated and obj.user == request.user
        return False
