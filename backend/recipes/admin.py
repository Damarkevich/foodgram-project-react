from django.contrib import admin

from .models import (Favorites, Follow, Ingredient, Recipe,
                     RecipeAndIngredient, ShoppingCart, Tag)


class RecipeAndIngredientInline(admin.TabularInline):
    model = RecipeAndIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('author', 'name', 'tags')

    def favorites_count(self, obj):
        return Favorites.objects.filter(recipe=obj).count()
    favorites_count.short_description = 'Add to favorites, times'


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(RecipeAndIngredient)
admin.site.register(Follow)
admin.site.register(Favorites)
admin.site.register(ShoppingCart)
