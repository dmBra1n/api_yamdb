from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Чтение и изменение контента доступны только для админа."""
    def has_permission(self, request, view):
        return (request.user.is_authenticated and request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение для чтения контента для всех пользователей
    и для изменения контента только для админа.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin)


class IsAuthorOrModeratorOrAdminOrReadOnly(permissions.BasePermission):
    """
    Чтение контента доступно любому пользователю.
    Изменение: автору, модератору, админу (в т.ч. суперюзеру).
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin)
