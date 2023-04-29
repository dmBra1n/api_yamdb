from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.conf import settings
from rest_framework import status, viewsets, mixins, filters
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title
from users.models import User
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    TitleWriteSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    MeSerializer,
    RegistrationSerializer,
    GetTokenSerializer,
)
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdminOrReadOnly
)
from .filters import TitleFilter


class ListCreateDestroyViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    Вьюсет для просмотра, создания и удаления категорий.
    Пользователи с правами администратора могут создавать,
    изменять и удалять категории.
    Пользователи без прав администратора могут только просматривать категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    """
    Только пользователи с правами администратора могут выполнять
    действия, которые изменяют данные (POST, PUT, PATCH, DELETE).
    Любой пользователь может просматривать данные (GET).
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    lookup_field = 'slug'


class TitleViewSet(ListCreateDestroyViewSet, mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin):
    """
    Любой пользователь может просматривать данные объекта,
    но только администраторы могут вносить изменения.
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleWriteSerializer


class ReviewViewSet(ListCreateDestroyViewSet, mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin):
    """
    Только зарегистрированные пользователи могут создавать, просматривать,
    обновлять и удалять отзывы.
    """

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdminOrReadOnly
    )

    def get_title(self, **kwargs):
        title_id = kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        title = self.get_title(**self.kwargs)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title(**self.kwargs)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ListCreateDestroyViewSet, mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin):
    """
    Только аутентифицированные пользователи могут взаимодействовать
    с комментариями.
    """
    serializer_class = CommentSerializer

    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdminOrReadOnly
    )

    def get_review(self, **kwargs):
        title_id = kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        review_id = kwargs.get('review_id')
        return get_object_or_404(title.reviews, id=review_id)

    def get_queryset(self):
        review = self.get_review(**self.kwargs)
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review(**self.kwargs)
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    """
    Только администраторы могут просматривать, создавать
    и обновлять пользователей.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^username',)
    lookup_field = 'username'


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Доступ к данной функции имеют только авторизованные пользователи.
    """
    if request.method == 'PATCH':
        serializer = MeSerializer(request.user, data=request.data,
                                  partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer = MeSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
def user_signup(request):
    """Регистрация users, генерация и отправка кода на почту"""
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        raise ValidationError(
            'username или email уже используются', status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация на Yamdb.',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(('POST',))
def get_token(request):
    """Выдача токена."""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data.get('username'))
    confirmation_code = serializer.data.get('confirmation_code')
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            'Код подтверждения неверный',
            status=status.HTTP_400_BAD_REQUEST
        )
    token = AccessToken.for_user(user)
    return Response(
        {'Token': str(token)},
        status=status.HTTP_200_OK
    )
