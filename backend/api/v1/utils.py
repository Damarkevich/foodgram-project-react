from django.http import HttpResponse

from recipes.models import Recipe, RecipeAndIngredient, ShoppingCart


def get_shopping_cart(user):
    ingredient_list = [f'{user.username}` shopping cart.\n\n']
    ingredient_dict = {}
    shopping_cart = ShoppingCart.objects.filter(user=user)
    for wanna_recipe in shopping_cart:
        recipe = Recipe.objects.get(id=wanna_recipe.recipe.id)
        ingredients = RecipeAndIngredient.objects.filter(recipe=recipe)
        for ingredient in ingredients:
            ingredient_dict[
                f'{ingredient.ingredient.name}'
                f'({ingredient.ingredient.measurement_unit})'
                ] = ingredient.amount + ingredient_dict.setdefault(
                    f'{ingredient.ingredient.name}'
                    f'({ingredient.ingredient.measurement_unit})', 0
                    )
    for key, value in ingredient_dict.items():
        ingredient_list.append(f'{key} - {value}\n')
    content = ingredient_list
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment'
    return response
