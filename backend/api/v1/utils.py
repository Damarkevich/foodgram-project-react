from recipes.models import Recipe, ShoppingCard, RecipeAndIngredient
from django.http import HttpResponse


def get_shopping_cart(user):
    file_name = f'shopping_cart_{user.username}.txt'
    ingredient_list = [f'{user.username}` shopping cart.\n\n']
    ingredient_dict = {}
    shopping_cart = ShoppingCard.objects.filter(user=user)
    for wanna_recipe in shopping_cart:
        recipe = Recipe.objects.get(id=wanna_recipe.recipe.id)
        ingredients = RecipeAndIngredient.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            ingredient_dict[
                f'{ingredient.ingredient.name} ({ingredient.ingredient.measurement_unit})'
                ] = ingredient.amount + ingredient_dict.setdefault(
                    f'{ingredient.ingredient.name} ({ingredient.ingredient.measurement_unit})', 0
                    )
    for key, value in ingredient_dict.items():
        ingredient_list.append(f'{key} - {value}\n')
    content = ingredient_list
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
