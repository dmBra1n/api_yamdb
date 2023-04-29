from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "redoc/",
        TemplateView.as_view(template_name="redoc.html"),
        name="redoc",
    ),
    path("api/", include("api.urls")),
]

"""
Список URL-адресов для проекта.

Примеры использования:
- /admin/ - URL-адрес для административного интерфейса Django.
- /redoc/ - URL-адрес для страницы документации API с помощью Redoc.
- /api/ - URL-адрес для доступа к API проекта.

"""
