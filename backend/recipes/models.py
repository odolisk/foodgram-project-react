from django.db import models
from django.db.models import F, Q
from django.core.validators import MinValueValidator

from colorfield.fields import ColorField

from users.models import User


class Tag(models.Model):

    name = models.CharField(
        verbose_name='Имя тега',
        max_length=50,
        help_text='Введите имя тега',
        unique=True
    )

    color = ColorField(
        verbose_name='Цвет в виде #000000',
        help_text='Введите цвет тега (в виде #000000)',
        unique=True
    )

    slug = models.SlugField(
        verbose_name='Идентификатор тега',
        unique=True,
        help_text='Укажите идентификатор тега')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=150,
        help_text='Введите название ингредиента'
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=50,
        help_text='Введите единицу измерения',
        blank=True,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('pk', )

    def __str__(self):
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
    )

    name = models.CharField(
        verbose_name='Наименование',
        max_length=150,
        help_text='Введите наименование рецепта'
    )

    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
        help_text='Выберите изображение')

    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите краткое описание'
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Укажите ингредиенты',
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='Теги'
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, 'Время приготовления должно быть не меньше 1')
        ],
        default=1,
        help_text='Укажите время приготовления в мин (>1)'
    )

    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_for_ingredient'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_for_recipe'
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1, 'Количество не может быть меньше 1')
        ],
        default=1
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = "Ингредиенты рецепта"
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='recipe_ingredient',
            )
        ]

    def __str__(self):
        return 'Ингредиент'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
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


class Favourite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favourites',
        verbose_name='Пользователь избранного'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favour_recipe',
        verbose_name='Рецепт в избранном'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='recipe-users'),
        )

    def __str__(self):
        return f'{self.user} add {self.recipe} to favourites'


class ShoppingList(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Пользователь списка'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в списке'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique-list'),
        )

    def __str__(self):
        return f'{self.user} add {self.recipe} to list'
