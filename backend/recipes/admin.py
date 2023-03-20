from django.contrib import admin

from .models import Tag, Ingredient, Recipe, RecipeAndIngredient, Favorites, Follow, ShoppingCard

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(RecipeAndIngredient)
admin.site.register(Follow)
admin.site.register(Favorites)
admin.site.register(ShoppingCard)
