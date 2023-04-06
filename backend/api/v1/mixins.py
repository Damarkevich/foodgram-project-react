from django.shortcuts import get_object_or_404
from recipes.models import Favorites, Follow, ShoppingCart
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (RecipeShortRepresentationSerializer,
                          UserGetForSubscribeSerializer)

related_dict = {
    'favorite': (Favorites, 'recipe', RecipeShortRepresentationSerializer),
    'shopping_cart': (
        ShoppingCart,
        'recipe',
        RecipeShortRepresentationSerializer
    ),
    'subscribe': (Follow, 'author', UserGetForSubscribeSerializer),
}


class CreateDeleteRelatedMixinView(
    DestroyModelMixin,
    CreateModelMixin,
    GenericAPIView,
):
    '''
    Universal MixinView with logic to create and destroy
    related connections for a different models.
    '''
    permission_classes = (IsAuthenticated,)

    def post(self, request, instance_id, related):
        obj = get_object_or_404(self.queryset, id=instance_id)
        user = self.request.user
        related_model, field_name, serializer = related_dict[related]
        if not related_model.objects.get_or_create(
            user=user,
            **{field_name: obj}
        )[1]:
            raise serializers.ValidationError(
                f"The {field_name} has already been added to {related}."
            )
        serializer = serializer(obj, context={'request': request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, instance_id, related):
        obj = get_object_or_404(self.queryset, id=instance_id)
        user = self.request.user
        related_model, field_name, _ = related_dict[related]
        if not related_model.objects.filter(
            user=user,
            **{field_name: obj}
        ).delete()[0]:
            raise serializers.ValidationError(
                f"The {field_name} is not in {related}."
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
