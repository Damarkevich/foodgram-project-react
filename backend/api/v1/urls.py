from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeDetail, RecipeList,
                    RecipeRelatedView, ShoppingCartDownloadAPIView,
                    SubscribeViewSet, TagViewSet, UserRelatedView)

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
    path('recipes/<int:instance_id>/', RecipeDetail.as_view()),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDownloadAPIView.as_view()
    ),
    path(
        'recipes/<int:instance_id>/<str:related>/',
        RecipeRelatedView.as_view()
    ),
    path('users/<int:instance_id>/<str:related>/', UserRelatedView.as_view()),
]
