import random

from django.db import IntegrityError
from django.conf import settings
from rest_framework import status, viewsets, mixins, filters
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
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
    IsAuthorOrModerator,
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
    permission_classes = (IsAdminOrReadOnly,)
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
    permission_classes = (IsAdminOrReadOnly,)
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


class ReviewViewSet(ListCreateDestroyViewSet, mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin):
    serializer_class = ReviewSerializer

    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrModerator,)
    """
    Только зарегистрированные пользователи могут создавать, просматривать,
    обновлять и удалять отзывы.
    """
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
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrModerator)

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


class UserViewSet(ListCreateDestroyViewSet, mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin):
    """
    Только администраторы могут просматривать, создавать
    и обновлять пользователей.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
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


class UserSignUpView(APIView):
    """Регистрация users, генерация и отправка кода на почту"""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if User.objects.filter(
                username=request.data.get('user'),
                email=request.data.get('email')
        ).exists():
            return Response(request.data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        confirmation_code = str(random.randint(1000, 9999))
        try:
            user, create = User.objects.get_or_create(
                username=username,
                email=email,
                confirmation_code=confirmation_code
            )
        except IntegrityError:
            raise ValidationError('Неверное имя пользователя или email')
        send_mail(
            subject='Регистрация на Yamdb',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(APIView):
    """Выдача токена."""
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if user.confirmation_code != confirmation_code:
            return Response(
                'Неверный код подтверждения',
                status=status.HTTP_400_BAD_REQUEST
            )
        refresh = RefreshToken.for_user(user)
        return Response(
            {'access_token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
