from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    """Класс для описания категорий"""
    name = models.TextField(
        max_length=256,
        verbose_name='Category Name'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Category Slug'
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = 'Category'

    def ___str___(self):
        return self.name


class Genre(models.Model):
    """Класс для описания жанров"""
    name = models.TextField(
        max_length=256,
        verbose_name='Genre name'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Genre slug'
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = 'Genre'

    def ___str___(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Title name'
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Title year'
    )
    category = models.ForeignKey(
        Category, on_delete=models.DO_NOTHING, related_name="title",
        verbose_name='Title category'
    )
    genre = models.ManyToManyField(
        Genre,
        through="GenreTitle",
        verbose_name='Title genre'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Title description'
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = 'Title'


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Title in GenreTitle'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Genre in GenreTitle'
    )

    class Meta:
        verbose_name = 'GenreTitle'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Reviews Title'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Reviews Author'
    )
    pub_date = models.DateTimeField(
        'Reviews Pub Date',
        auto_now_add=True,
        db_index=True,
    )
    text = models.TextField(
        verbose_name='Reviews Text'
    )
    score = models.IntegerField(
        'Reviews Score',
        default=0,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name="unique_review")
        ]
        verbose_name = 'Reviews'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Comment Reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Comment Author'
    )
    pub_date = models.DateTimeField(
        'Comment Pub Date',
        auto_now_add=True,
        db_index=True,
    )
    text = models.TextField(
        verbose_name='Comment Text'
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = 'Comment'

    def __str__(self):
        return self.author
