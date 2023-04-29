from rest_framework.routers import DefaultRouter

from django.urls import include, path

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    GetTokenView,
    ReviewViewSet,
    TitleViewSet,
    UserSignUpView,
    UserViewSet,
    me_view,
)

app_name = "api"

# Создание роутера и регистрация ViewSet'ов
router = DefaultRouter()
router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("genres", GenreViewSet, basename="genre")
router.register("titles", TitleViewSet, basename="title")
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="review"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comment",
)
router.register("titles", TitleViewSet, basename="title")
router.register("users", UserViewSet, basename="user")

# Определение URL-шаблонов
registration_urlpatterns = [
    path("auth/signup/", UserSignUpView.as_view(), name="sign_up"),
    path("auth/token/", GetTokenView.as_view(), name="get_token"),
]

urlpatterns = [
    path("v1/", include(registration_urlpatterns)),  # URL-шаблоны регистрации
    path(
        "v1/users/me/", me_view
    ),  # URL для получения инфо о текущем пользователе
    path("v1/", include(router.urls)),  # URL-шаблоны API
]
