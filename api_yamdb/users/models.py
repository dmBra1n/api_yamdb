from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import validate_username


class User(AbstractUser):
    USER_ROLE_NAME = 'user'
    MODERATOR_ROLE_NAME = 'moderator'
    ADMIN_ROLE_NAME = 'admin'

    ROLES = [
        (USER_ROLE_NAME, 'User'),
        (MODERATOR_ROLE_NAME, 'Moderator'),
        (ADMIN_ROLE_NAME, 'Admin'),
    ]
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
        validators=(validate_username,),
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='Адрес электронной почты'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=30,
        default=USER_ROLE_NAME,
        choices=ROLES,
        verbose_name='Роль'
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR_ROLE_NAME

    @property
    def is_admin(self):
        return self.role == self.ADMIN_ROLE_NAME or self.is_superuser

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
