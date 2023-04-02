import csv

from django.db import migrations


def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model("recipes", "Ingredient")
    with open('../data/ingredients.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            new_ingredient = Ingredient(
                    name=row[0],
                    measurement_unit=row[1],
                )
            new_ingredient.save()


def remove_ingredients(apps, schema_editor):
    Ingredient = apps.get_model("ingredient")
    with open('../data/ingredients.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            Ingredient.objects.get(name=row[0]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_add_tags'),
    ]

    operations = [
        migrations.RunPython(
            add_ingredients,
            remove_ingredients,
        ),
    ]
