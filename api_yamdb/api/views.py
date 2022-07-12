from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import status, viewsets, views, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters import rest_framework as d_filters

from reviews.models import Review, Title, Category, Genre
from .paginator import DefaultPagination
from .permissions import (AuthorAndStaffOrReadOnly,
                          IsAdminOrReadOnly,
                          IsOwners,
                          IsAdmin)
from .serializers import (CommentsSerializer,
                          ReviewsSerializer,
                          TitleSerializer,
                          TitlePostSerializer,
                          CategorySerializer,
                          GenreSerializer,
                          UserCreateSerializer,
                          MyTokenObtainSerializer,
                          UserSerializer)
from .mixins import ReadOrCreateOrDeleteViewSet

User = get_user_model()


class TitleFilter(d_filters.FilterSet):
    category = d_filters.CharFilter(field_name="category__slug",
                                    lookup_expr='icontains')
    genre = d_filters.CharFilter(field_name="genre__slug")
    name = d_filters.CharFilter(field_name="name", lookup_expr='icontains')
    year = d_filters.NumberFilter(field_name="year")

    class Meta:
        model = Title
        fields = ["category", "genre", "name", "year"]


class CategoryViewSet(ReadOrCreateOrDeleteViewSet):
    queryset = Category.objects.all()
    lookup_field = 'slug'
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]


class GenreeViewSet(ReadOrCreateOrDeleteViewSet):
    queryset = Genre.objects.all()
    lookup_field = 'slug'
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    lookup_field = 'id'
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (d_filters.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewsSerializer
    pagination_class = DefaultPagination
    permission_classes = [AuthorAndStaffOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        new_queryset = title.reviews.all()
        return new_queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        if not title.reviews.filter(author=self.request.user).exists():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentsSerializer
    pagination_class = DefaultPagination
    permission_classes = [AuthorAndStaffOrReadOnly]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        if review in title.reviews.all():
            queryset = review.comments.all()
        else:
            raise KeyError('No Review to Comment')
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class UserAuthView(views.APIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    http_method_names = ['post', ]

    def post(self, validated_data):
        username = self.request.data.get('username')
        email = self.request.data.get('email')

        serializer = UserCreateSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            new_user = get_object_or_404(User, username=username)
            code = User.objects.make_random_password()
            new_user.set_password(code)
            new_user.save(update_fields=['password'])
            send_mail(
                f'Hello, {username} Confirm your email',
                f'Your confirmation code: {code}.',
                'info@yamdb.fake',
                [email],
                fail_silently=False,
            )

            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.data,
                        status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainView(views.APIView):
    def post(self, request):
        if not request.data.get("username"):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = MyTokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get("username")
        password = request.data.get("confirmation_code")
        user = get_object_or_404(User, username=username)
        if not user:
            return Response(data="User not found",
                            status=status.HTTP_404_NOT_FOUND)

        if authenticate(username=username, password=password):
            token = RefreshToken.for_user(user).access_token
            return Response(
                {"token": str(token)},
                status=status.HTTP_201_CREATED,
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    pagination_class = DefaultPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = [IsAdmin]

    @action(
        methods=["get", "patch"],
        detail=False,
        permission_classes=(IsOwners,),
        url_path="me",
    )
    def get_user_info(self, request):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=self.request.user.username)
        if (user.role == 'user'
                and request.data.get('role') in ['moderator', 'admin']):
            request.data._mutable = True
            request.data['role'] = 'user'
            request.data._mutable = False
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
