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


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allows only admins to create, edit and delete objects."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_staff
        )
