from http import HTTPStatus

from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from djoser import email
from djoser.serializers import ActivationSerializer, UserCreateSerializer
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import User
from .serializers import UserSerializer


class UserModelViewSet(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
):
    queryset = User.objects.all()

    def get_serializer_class(self):
        """Select serializer as required."""
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "activation":
            return ActivationSerializer
        return UserSerializer

    def perform_create(self, serializer) -> None:
        """Create user and send activation email."""
        user_email = self.request.data["email"]
        serializer.save(email=user_email)

        user = User.objects.get(email=user_email)
        context = {"user": user}
        email.ActivationEmail(self.request, context).send([user_email])

    @action(
        methods=["post"],
        detail=False,
    )
    def resend_activation(self, request) -> Response:
        user = request.user
        if not user.is_active:
            email.ActivationEmail(
                self.request,
                {"user": user},
            ).send([user.email])
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        methods=["get"],
        detail=False,
        url_path="activation/<uid>/<token>",
        permission_classes=(AllowAny,),
    )
    def activation(self, request, uid=None, token=None) -> Response:
        """Activate user by email link"""
        try:
            decoded_uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=decoded_uid)
        except ObjectDoesNotExist:
            user = None
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return Response(status=HTTPStatus.OK)
        return Response(status=HTTPStatus.UNAUTHORIZED)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,),  # TODO: Set permissions
    )
    def me(self, request) -> Response:
        """Show user's self data."""
        return Response(self.get_serializer(request.user).data)

    @me.mapping.patch
    def patch_me(self, request) -> Response:
        """Update current user's data."""
        breakpoint()
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


#
# class PasswordViewSet(GenericViewSet):
#     queryset = User.objects.all()
#
#     def get_serializer_class(self):
#         if self.action == "reset_password":
#             return djoser_settings.SERIALIZERS.password_reset
#         if self.action == "reset_password_confirm":
#             if djoser_settings.PASSWORD_RESET_CONFIRM_RETYPE:
#                 return djoser_settings.SERIALIZERS.password_reset_confirm_retype
#             return djoser_settings.SERIALIZERS.password_reset_confirm
#         if self.action == "set_password":
#             if djoser_settings.SET_PASSWORD_RETYPE:
#                 return djoser_settings.SERIALIZERS.set_password_retype
#             return djoser_settings.SERIALIZERS.set_password
#         return None
#
#     @action(["post"], detail=False)
#     def set_password(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         self.request.user.set_password(serializer.data["new_password"])
#         self.request.user.save()
#
#         if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
#             context = {"user": self.request.user}
#             to = [compat.get_user_email(self.request.user)]
#             djoser_settings.EMAIL.password_changed_confirmation(
#             self.request, context).send(to)
#
#         if djoser_settings.LOGOUT_ON_PASSWORD_CHANGE:
#             logout(self.request)
#         elif djoser_settings.CREATE_SESSION_ON_LOGIN:
#             update_session_auth_hash(self.request, self.request.user)
#         return Response(status=HTTPStatus.NO_CONTENT)
#
#     @action(["post"], detail=False)
#     def reset_password(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.get_user()
#
#         if user:
#             context = {"user": user}
#             to = [compat.get_user_email(user)]
#             djoser_settings.EMAIL.password_reset(self.request, context).send(to)
#
#         return Response(status=HTTPStatus.NO_CONTENT)
#
#     @action(["post"], detail=False)
#     def reset_password_confirm(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         serializer.user.set_password(serializer.data["new_password"])
#         if hasattr(serializer.user, "last_login"):
#             serializer.user.last_login = now()
#         serializer.user.save()
#
#         if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
#             context = {"user": serializer.user}
#             to = [compat.get_user_email(serializer.user)]
#             djoser_settings.EMAIL.password_changed_confirmation(
#                 self.request, context).send(to)
#         return Response(status=HTTPStatus.NO_CONTENT)
