from djoser.serializers import UserCreateSerializer
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer
from applications.helpers import create_notification_settings


class UserModelViewSet(CreateModelMixin, GenericViewSet):
    """
    ViewSet that works with User model.
    Allows to create user (no auth required),
    get and update one's own info (auth required).
    """

    queryset = User.objects.all()
    http_method_names = ["get", "post", "patch"]

    def get_serializer_class(self):
        """Select serializer as required."""
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "patch_me":
            return UserUpdateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        """Triggers creation of notification settings object linked to this new user."""
        serializer.save()
        created_user = serializer.instance
        create_notification_settings(user=created_user)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request) -> Response:
        """Show user's self data."""
        return Response(self.get_serializer(request.user).data)

    @me.mapping.patch
    def patch_me(self, request) -> Response:
        """Update current user's data."""
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
