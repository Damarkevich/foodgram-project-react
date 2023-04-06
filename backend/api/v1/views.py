from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Follow, Ingredient, Recipe, Tag
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

from .filter import IngredientFilter, RecipeFilter
from .mixins import CreateDeleteRelatedMixinView
from .permissions import IsOwner, IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, TagSerializer,
                          UserGetForSubscribeSerializer)
from .utils import get_shopping_cart


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset with logic for displaying a list or single tags.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset with logic for displaying a list or single ingredients.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeList(generics.ListCreateAPIView):
    '''View with logic for displaying a list and creating recipes.'''
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart:
            is_in_shopping_cart = int(is_in_shopping_cart)
        if (user.is_authenticated and is_in_shopping_cart):
            return queryset.filter(shopping_cart__user=user)
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            is_favorited = int(is_favorited)
        if (user.is_authenticated and is_favorited):
            return queryset.filter(favorites__user=user)
        return queryset

    def post(self, request):
        serializer = RecipeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        saved_obj = serializer.save(author=self.request.user)
        response_data = RecipeSerializer(
            saved_obj,
            context={'request': request}
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    '''RUD logic for a single recipe.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_url_kwarg = 'instance_id'

    def partial_update(self, request, instance_id):
        recipe = get_object_or_404(Recipe, id=instance_id)
        serializer = RecipeCreateSerializer(
            recipe,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        saved_obj = serializer.save()
        response_data = RecipeSerializer(
            saved_obj,
            context={'request': request}
        ).data
        return Response(
            response_data,
            status=status.HTTP_205_RESET_CONTENT
        )


class SubscribeViewSet(viewsets.ReadOnlyModelViewSet):
    '''Viewset with logic to display current user's subscriptions.'''
    serializer_class = UserGetForSubscribeSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        user = self.request.user
        subscriptions = Follow.objects.filter(user=user)
        user_list = []
        for subscription in subscriptions:
            user_list.append(subscription.author)
        return user_list


class RecipeRelatedView(CreateDeleteRelatedMixinView):
    '''
    View with logic to create and destroy related connection
    (add to favorite or to shopping cart) for single recipe.
    '''
    queryset = Recipe.objects.all()


class UserRelatedView(CreateDeleteRelatedMixinView):
    '''
    View with logic to create and destroy related connection
    (add to favorite) for single user.
    '''
    queryset = User.objects.all()


class ShoppingCartDownloadAPIView(APIView):
    '''
    View with logic to download list of ingredients for recipes from cart.
    '''
    permission_classes = (IsOwner,)

    def get(self, request):
        return get_shopping_cart(self.request.user)
