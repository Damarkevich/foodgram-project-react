from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteAPIView, IngredientViewSet, RecipeDetail,
                    RecipeList, ShoppingCartAPIView,
                    ShoppingCartDownloadAPIView, SubscribeAPIView,
                    SubscribeViewSet, TagViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(
    r'users/subscriptions',
    SubscribeViewSet,
    basename='subscriptions'
)


urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/', RecipeList.as_view()),
    path('recipes/<int:pk>/', RecipeDetail.as_view()),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDownloadAPIView.as_view()
    ),
    path('recipes/<int:pk>/favorite/', FavoriteAPIView.as_view()),
    path('recipes/<int:pk>/shopping_cart/', ShoppingCartAPIView.as_view()),
    path('users/<int:pk>/subscribe/', SubscribeAPIView.as_view()),
]