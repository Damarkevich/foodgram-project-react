from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (Favorites, Follow, Ingredient, Recipe,
                            ShoppingCart, Tag)
from users.models import User

from .filter import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly, Owner
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeGetWithFavoriteSerializer, RecipeSerializer,
                          TagSerializer, UserGetForSubscribeSerializer)
from .utils import get_shopping_cart


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeList(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = self.request.query_params.get('is_favorited')
        if (user.is_authenticated and is_in_shopping_cart == '1'):
            return queryset.filter(shopping_cart__user=user)
        if (user.is_authenticated and is_favorited == '1'):
            return queryset.filter(favorites__user=user)
        return queryset

    def post(self, request):
        serializer = RecipeCreateSerializer(data=request.data)
        if serializer.is_valid():
            saved_obj = serializer.save(author=self.request.user)
            response_data = RecipeSerializer(
                saved_obj,
                context={'request': request}
            ).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def partial_update(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeCreateSerializer(
            recipe,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            saved_obj = serializer.save()
            response_data = RecipeSerializer(
                saved_obj,
                context={'request': request}
            ).data
            return Response(
                response_data,
                status=status.HTTP_205_RESET_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class FavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "The recipe has already been added to favorites."
            )
        Favorites.objects.get_or_create(user=user, recipe=recipe)
        serializer = RecipeGetWithFavoriteSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if not Favorites.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "The recipe is not in favorites."
            )
        Favorites.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        author = get_object_or_404(User, id=pk)
        user = self.request.user
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                "The author has already been added to subscriptions."
            )
        if user == author:
            raise serializers.ValidationError(
                "You can't subscribe to yourself."
            )
        Follow.objects.get_or_create(user=user, author=author)
        serializer = UserGetForSubscribeSerializer(author)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, id=pk)
        user = self.request.user
        if not Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                "The author is not in subscriptions."
            )
        Follow.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserGetForSubscribeSerializer
    permission_classes = [Owner]

    def get_queryset(self):
        user = self.request.user
        subscriptions = Follow.objects.filter(user=user)
        user_list = []
        for subscription in subscriptions:
            user_list.append(subscription.author)
        return user_list


class ShoppingCartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None 

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "The recipe is already on the shopping cart."
            )
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        serializer = RecipeGetWithFavoriteSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "The recipe is not on the shopping cart."
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadAPIView(APIView):
    permission_classes = [Owner]

    def get(self, request):
        return get_shopping_cart(self.request.user)
