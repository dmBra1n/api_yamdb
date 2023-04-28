from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet,
    UserViewSet,
    me_view,
    UserSignUpView,
    GetTokenView,

)
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
    path('auth/signup/', UserSignUpView.as_view(), name='sign_up'),
    path('auth/token/', GetTokenView.as_view(), name='get_token')
]

urlpatterns = [
    # path('v1/api-token-auth/', views.obtain_auth_token),
    path('v1/', include(registration_urlpatterns)),
    path('v1/users/me/', me_view),
    path('v1/', include(router.urls)),

]
