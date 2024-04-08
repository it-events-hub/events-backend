from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password

# TODO: move to users.utils
SUPERUSER_FIELDS_ERROR = (
    "Суперпользователь должен иметь is_staff=True, is_superuser=True и is_active=True."
)
REQUIRED_FIELDS_ERROR = (
    "Поля email, phone, first_name, last_name обязательны для заполнения."
)


class MyUserManager(BaseUserManager):
    """Custom manager for the User model."""

    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: str,
        **extra_fields
    ):
        """Saves a user having email, phone, first name, last_name and password."""
        if not all([email, phone, first_name, last_name]):
            raise ValueError(REQUIRED_FIELDS_ERROR)
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        email: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: str = None,
        **extra_fields
    ):
        """Sets defaults for an ordinary user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)
        return self._create_user(
            email=email,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

    def create_superuser(
        self,
        email: str,
        phone: str,
        first_name: str,
        last_name: str,
        password: str = None,
        **extra_fields
    ):
        """Sets defaults for a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not all(
            [
                extra_fields.get("is_staff"),
                extra_fields.get("is_superuser"),
                extra_fields.get("is_active"),
            ]
        ):
            raise ValueError(SUPERUSER_FIELDS_ERROR)
        return self._create_user(
            email=email,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
