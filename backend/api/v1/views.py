from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from recipes.models import Tag, Ingredient, Recipe, Favorites, Follow, ShoppingCard
from users.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view  # Импортировали декоратор
from rest_framework.response import Response  # Импортировали класс Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import HttpResponse, HttpResponseNotFound

#from .filter import TitleFilter
from .mixins import CreateDestroyListViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsOwnerModeratorAdminOrReadOnly, Owner)
from .utils import get_shopping_cart
from djoser.views import UserViewSet
from .serializers import CustomUserSerializer, UserGetForSubscribeSerializer, CustomUserCreateSerializer, FavoriteSerializer, RecipeGetWithFavoriteSerializer, TagSerializer, RecipeSerializer, IngredientSerializer, RecipeCreateSerializer



class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None 


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class FavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        Favorites.objects.get_or_create(user=user, recipe=recipe)
        serializer = RecipeGetWithFavoriteSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        Favorites.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, pk):
        author = get_object_or_404(User, id=pk)
        user = self.request.user
        Follow.objects.get_or_create(user=user, author=author)
        serializer = UserGetForSubscribeSerializer(author)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        author = get_object_or_404(User, id=pk)
        user = self.request.user
        Follow.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserGetForSubscribeSerializer
    permission_classes = [Owner,]

    def get_queryset(self):
        user = self.request.user
        subscriptions = Follow.objects.filter(user=user)
        user_list = []
        for subscription in subscriptions:
            user_list.append(subscription.author)
        return user_list


class ShoppingCartAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        ShoppingCard.objects.get_or_create(user=user, recipe=recipe)
        serializer = RecipeGetWithFavoriteSerializer(recipe)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = self.request.user
        ShoppingCard.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadAPIView(APIView):
    permission_classes = [Owner,]

    def get(self, request):
        user = self.request.user
        shopping_cart_file = get_shopping_cart(user)
        return shopping_cart_file