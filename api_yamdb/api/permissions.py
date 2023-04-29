from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение только для админа на изменение контента."""

    def has_permission(self, request, view):
        """Проверяет, имеет ли пользователь права на изменение контента."""
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение для чтения контента для всех пользователей
    и для изменения контента только для админа.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь права
        на чтение или изменение контента.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorOrModerator(permissions.BasePermission):
    """
    Разрешение на изменение контента только для автора и модератора.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь права на чтение
        или изменение контента.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь права на чтение или изменение объекта.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
        )
