from django.db import models

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Класс для расширения стандартной модели user
    """
    avatar = models.ImageField(blank=True, null=True, upload_to='users/%Y/%m/%d', verbose_name='Аватар')
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name='Возраст')
    interests = models.TextField(blank=True, null=True, verbose_name='Интересы')


