from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    CHOICES = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор '),
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(max_length=300, choices=CHOICES, default='user')

    class Meta:
        ordering = ["-id"]

    def is_admin(self):
        return self.role == 'admin'

    def is_moderator(self):
        return self.role == 'moderator'
