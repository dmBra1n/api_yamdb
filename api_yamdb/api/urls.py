from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, get_token,
                    me_view, user_signup)

app_name = 'api'

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('genres', GenreViewSet, basename='genre')
router.register('titles', TitleViewSet, basename='title')
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router.register('titles', TitleViewSet, basename='title')
router.register('users', UserViewSet, basename='user')

registration_urlpatterns = [
    path('auth/signup/', user_signup, name='sign_up'),
    path('auth/token/', get_token, name='get_token')
]

urlpatterns = [
    path('v1/', include(registration_urlpatterns)),
    path('v1/users/me/', me_view),
    path('v1/', include(router.urls)),
]
