from http import HTTPStatus

from django.contrib.auth import logout, update_session_auth_hash
from django.utils.timezone import now

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser.serializers import UserCreateSerializer
from djoser import compat, signals
from djoser.conf import settings

from .models import User
from .serializers import UserSerializer


class UserModelViewSet(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer) -> None:
        serializer.save(email=self.request.data["email"])

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,),  # TODO: Set permissions
    )
    def me(self, request) -> Response:
        return Response(self.get_serializer(request.user))

    @me.mapping.delete
    def del_me(self, request) -> Response:
        user = request.user
        logout(request)
        user.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @me.mapping.patch
    def patch_me(self, request) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ActivationViewSet(GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "activation":
            return settings.SERIALIZERS.activation
        elif self.action == "resend_activation":
            return settings.SERIALIZERS.password_reset

    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        signals.user_activated.send(
            sender=self.__class__, user=user, request=self.request
        )

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [compat.get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(status=HTTPStatus.NO_CONTENT)

    @action(["post"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user(is_active=False)

        if not settings.SEND_ACTIVATION_EMAIL:
            return Response(status=HTTPStatus.BAD_REQUEST)

        if user:
            context = {"user": user}
            to = [compat.get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)

        return Response(status=HTTPStatus.NO_CONTENT)


class PasswordViewSet(GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "reset_password":
            return settings.SERIALIZERS.password_reset
        elif self.action == "reset_password_confirm":
            if settings.PASSWORD_RESET_CONFIRM_RETYPE:
                return settings.SERIALIZERS.password_reset_confirm_retype
            return settings.SERIALIZERS.password_reset_confirm
        elif self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [compat.get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            logout(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(["post"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()

        if user:
            context = {"user": user}
            to = [compat.get_user_email(user)]
            settings.EMAIL.password_reset(self.request, context).send(to)

        return Response(status=HTTPStatus.NO_CONTENT)

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [compat.get_user_email(serializer.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)
        return Response(status=HTTPStatus.NO_CONTENT)
