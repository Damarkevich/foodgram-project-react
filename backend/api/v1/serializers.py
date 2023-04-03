from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorites, Follow, Ingredient, Recipe,
                            RecipeAndIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import User


class RecipeGetWithFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserGetForSubscribeSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeGetWithFavoriteSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    def get_is_subscribed(self, value):
        return True

    def get_recipes_count(self, value):
        return Recipe.objects.filter(author=value).count()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, value):
        user = self.context['request'].user
        if user.is_authenticated and Follow.objects.filter(
            user=user,
            author=value
        ).exists():
            return True
        return False

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        lookup_field = 'slug'


class IngredientsWithAmountSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeAndIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeAndIngredient
        fields = (
            'ingredient',
            'id',
            'amount'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientAmountSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            RecipeAndIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data.get('ingredient'),
                amount=ingredient_data.get('amount')
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        Recipe.objects.filter(id=instance.id).update(**validated_data)
        recipe = Recipe.objects.get(id=instance.id)
        recipe.tags.set(tags)
        rec_ing_for_deleting = RecipeAndIngredient.objects.filter(
            recipe=recipe
        )
        rec_ing_for_deleting.delete()
        for ingredient_data in ingredients_data:
            RecipeAndIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data.get('ingredient'),
                amount=ingredient_data.get('amount')
            )
        return recipe


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(required=True, many=False)
    ingredients = IngredientsWithAmountSerializer(
        source='ingredients_with_amount_set',
        many=True
    )
    tags = TagSerializer(required=False, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shoping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, value):
        user = self.context['request'].user
        if user.is_authenticated and Favorites.objects.filter(
            user=user,
            recipe=value
        ).exists():
            return True
        return False

    def get_is_in_shoping_cart(self, value):
        user = self.context['request'].user
        if user.is_authenticated and ShoppingCart.objects.filter(
            user=user,
            recipe=value
        ).exists():
            return True
        return False

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shoping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = (
            'user',
            'recipe',
        )
