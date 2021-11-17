from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    email = models.EmailField(
        'email',
        unique=True,
        help_text='Email адрес. Должен быть уникальным.',
        error_messages={
            'unique': 'Пользователь с таким Email уже существует.',
        })
    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        help_text=('Обязательное поле. Не более 150 символов. '
                   'Буквы, цифры и символы @/./+/-/_'),
        validators=[username_validator],
        error_messages={
            'unique': 'Пользователь с таким логином уже существует.',
        },
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        help_text='Обязательное поле. Не более 150 символов.')
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        help_text='Обязательное поле. Не более 150 символов.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subs_subscribers',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subs_authors',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='subscript-users'),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='prevent_self_subscribe'),
        )

    def __str__(self):
        return f'{self.user.username} to {self.author.username}'
