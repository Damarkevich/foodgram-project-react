from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=100,
        blank=False,
        null=False,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=100,
        blank=False,
        null=False,
        unique=True,
    )
    color = ColorField(
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Name',
        max_length=100,
        blank=False,
        null=False,
        help_text='Enter ingredient name'
    )
    measurement_unit = models.CharField(
        verbose_name='Measurement unit',
        max_length=100,
        blank=False,
        null=False,
        default='kg',
        help_text='Enter measurement unit'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ['name']


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author',
        help_text='Enter recipe author'
    )
    name = models.CharField(
        verbose_name='Name',
        max_length=100,
        help_text='Enter recipe name'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        blank=True,
    )
    text = models.TextField(
        verbose_name='Description',
        help_text='Enter recipe description'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tag',
        related_name='recipes',
        help_text='Choose tags'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeAndIngredient',
        help_text='Choose ingredients'
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True,
        db_index=True,
        help_text='Enter publication date',
    )
    cooking_time = models.IntegerField(
        verbose_name='cooking time',
        blank=False,
        null=False,
        help_text='Enter cooking time',
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f'{self.name} - {self.author}'

    class Meta:
        ordering = ['-pub_date']


class RecipeAndIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients_with_amount_set',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        verbose_name='Amount',
        blank=False,
        null=False,
        help_text='Enter amount',
    )

    def __str__(self):
        return (
            f'Recipe - {self.recipe}',
            f'Ingredient - {self.ingredient}',
            f'Amount - {self.amount}'
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower',
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Author',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='author_user_unique'
            ),
        ]


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_favorites',
        verbose_name='Users favorites',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recipe',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='author_recipe_favorites_unique'
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='users_shopping_cart',
        verbose_name='Users shopping cart',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Recipe',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='author_recipe_shopping_cart_unique'
            ),
        ]
