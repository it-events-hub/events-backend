from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from applications.views import ApplicationViewSet, NotificationSettingsAPIView
from events.views import EventViewSet
from users.views import ActivationViewSet, PasswordViewSet, UserModelViewSet

# from rest_framework_simplejwt import views
# from djoser.urls import base


app_name = "api"

router = DefaultRouter()
router.register("users", UserModelViewSet, "users")
router.register("users", ActivationViewSet, "activation")
router.register("users", PasswordViewSet, "password")
router.register("events", EventViewSet, "events")
router.register("applications", ApplicationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.jwt")),
    path("notification_settings/<int:pk>/", NotificationSettingsAPIView.as_view()),
]

schema_view = get_schema_view(
    openapi.Info(
        title="Hackathon Yandex Funtech Team 02 API",
        default_version="v1",
        description="API documentation for the Hackathon Yandex Funtech project",
        # terms_of_service="URL страницы с пользовательским соглашением",
        contact=openapi.Contact(email="hackathonyacrm@yandex.kz"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
