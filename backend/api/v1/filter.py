from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag

BOOLEAN_CHOICES = ((0, 'False'), (1, 'True'),)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
        ]
