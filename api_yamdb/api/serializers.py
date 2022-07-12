from django.utils.timezone import now
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.db.models import Avg

from reviews.models import (
    Title,
    Category,
    Genre,
    Comment,
    Review,
    GenreTitle,
)

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class GenreTitleSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='genre.name')
    slug = serializers.ReadOnlyField(source='genre.slug')

    class Meta:
        model = GenreTitle
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category"""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreTitleSerializer(source='genretitle_set', many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('__all__')

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        return rating


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field="slug", many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", many=False, queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )

    def validate_year(self, value):
        if value > now().year:
            raise serializers.ValidationError(
                "Год должен быть не больше текущего."
            )
        return value


class ReviewsSerializer(serializers.ModelSerializer):
    """Ревью для произведений"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ['title']

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title_id = (
                self.context['request'].parser_context['kwargs']['title_id']
            )
            user = self.context['request'].user
            if user.reviews.filter(title_id=title_id).exists():
                raise serializers.ValidationError(
                    'Нельзя оставить отзыв на одно произведение дважды'
                )
        return data

    def validate_score(self, value):
        if 0 >= value >= 10:
            raise serializers.ValidationError('Проверьте оценку')
        return value


class CommentsSerializer(serializers.ModelSerializer):
    """Комментарии на отзывы"""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        fields = ('email', 'username')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Cannot create user with username="me"')
        check_query = User.objects.filter(username=value)
        if check_query.exists():
            raise serializers.ValidationError(
                'Cannot create a user whose username is already in use')
        return value

    def validate_email(self, value):
        check_query = User.objects.filter(email=value)
        if check_query.exists():
            raise serializers.ValidationError(
                'Cannot create a user whose email is already in use')
        return value


class MyTokenObtainSerializer(serializers.ModelSerializer):
    confirmation_code = SlugRelatedField(slug_field='password', read_only=True)

    class Meta:
        fields = ('username', 'confirmation_code')
        read_only_fields = ('username', 'confirmation_code')
        model = User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_email(self, value):
        check_query = User.objects.filter(email=value)
        if check_query.exists():
            raise serializers.ValidationError(
                'Cannot create a user whose email is already in use')
        return value
