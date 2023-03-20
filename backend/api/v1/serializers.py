from django.shortcuts import get_object_or_404
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe, RecipeAndIngredient, Follow, Favorites, ShoppingCard
from users.models import User
from djoser.serializers import UserSerializer, UserCreateSerializer, TokenCreateSerializer
import base64
from django.core.files.base import ContentFile
from drf_extra_fields.fields import Base64ImageField


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
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class CustomTokenCreateSerializer(TokenCreateSerializer):
    class Meta:
        model = User
        fields = ('password', 'email')


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


class IngredientForRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id',)

class ImageField(serializers.Field):

    def to_internal_value(self, value):
        image_str = value['image']
        format, imgstr = image_str.split(';base64,')
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return image


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientForRecipeSerializer(many=True)
 
    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):
        # Уберем список достижений из словаря validated_data и сохраним его
        ingredients = validated_data.pop('ingredients')

        # Создадим нового котика пока без достижений, данных нам достаточно
        recipe = Recipe.objects.create(**validated_data)

        # Для каждого достижения из списка достижений
        for ingredient in ingredients:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient)
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            RecipeAndIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=ingredient.amount)
        return recipe



class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(required=True, many=False)
    ingredients = IngredientsWithAmountSerializer(source='ingredients_with_amount_set', many=True)
    tags = TagSerializer(required=False, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shoping_card = serializers.SerializerMethodField()

    def get_is_favorited(self, value):
        user = self.context['request'].user
        if user.is_authenticated and Favorites.objects.filter(
            user=user,
            recipe=value
        ).exists():
            return True
        return False

    def get_is_in_shoping_card(self, value):
        user = self.context['request'].user
        if user.is_authenticated and ShoppingCard.objects.filter(
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
            'is_in_shoping_card',
            'name',
            'image',
            'text',
            'cooking_time'
        )
#        lookup_field = 'id'


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = (
            'user',
            'recipe',
        )



'''

class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        )


class TitleReadOnlySerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField()

    def validate(self, value):
        if self.context['request'].method != 'POST':
            return value

        author = self.context['request'].user
        title_id = (self.context['request'].
                    parser_context['kwargs'].get('title_id'))
        title = get_object_or_404(Title, id=title_id)

        if title.reviews.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                f'Отзыв на произведение {title.name} уже существует'
            )
        return value

    class Meta:
        fields = ('id', 'author', 'text', 'score', 'title', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'author', 'text', 'review', 'pub_date')
        model = Comment

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class UserPatchSerializer(UserSerializer):
    role = serializers.PrimaryKeyRelatedField(read_only=True)


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, allow_blank=False)
    email = serializers.EmailField(allow_blank=False)

    def validate(self, data):
        email = data['email'].lower()
        username = data['username'].lower()
        if User.objects.filter(username=username, email=email).exists():
            return data
        if username == 'me':
            raise serializers.ValidationError('Нельзя использовать имя "me"!')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                f"Пользователь с username {username} уже зарегистрирован!"
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                f"Пользователь с email {email} уже зарегистрирован!"
            )
        return data


class CreateTokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, allow_blank=False)
    confirmation_code = serializers.CharField(max_length=50, allow_blank=False)
'''