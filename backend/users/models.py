from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        'email',
        unique=True,
        help_text='Email адрес. Должен быть уникальным.',
        error_messages={
            'unique': 'Пользователь с таким Email уже существует.',
        })
    first_name = models.CharField(
        'Имя',
        max_length=150,
        help_text='Обязательное поле. Не более 150 символов.')
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        help_text='Обязательное поле. Не более 150 символов.'
        )

    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)
