from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from .models import User
from .serializers import UserSerializer


class UserModelViewSet(ModelViewSet):  # TODO: change to explicit mixins
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (...,)

    # ******************
    # Список эндпойнтов:
    # 1. POST /users/
    # 2. GET /users/me/
    # 3. PATCH /users/me/
    # 4. DELETE /users/me/
    # Под вопросом:
    # 5. GET /users/
    # 6. POST /users/activation/
    # 7. POST /users/resend_activation/
    # 8. POST /users/reset_password/
    # 9. POST /users/reset_password_confirm/
    # 10. POST /users/set_password/
    # JWT:
    # 11. /auth/jwt/create/
    # 12. /auth/jwt/refresh/
    # 13. /auth/jwt/verify/
    # **********************

    # @action(
    #     methods=('post',),
    #     # detail=...,
    #     # permission_classes=(...,),
    # )
    # def login(self, request):
    #     return ...
