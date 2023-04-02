from django.db import migrations

INITIAL_TAGS = [
    {'color': '#FFA84F', 'name': 'Breakfast', 'slug': 'breakfast'},
    {'color': '#00FF00', 'name': 'Lunch', 'slug': 'lunch'},
    {'color': '#FF67FA', 'name': 'Dinner', 'slug': 'dinner'},
]


def add_tags(apps, schema_editor):
    Tag = apps.get_model("recipes", "Tag")
    for tag in INITIAL_TAGS:
        new_tag = Tag(**tag)
        new_tag.save()


def remove_tags(apps, schema_editor):
    Tag = apps.get_model("Tag")
    for tag in INITIAL_TAGS:
        Tag.objects.get(slug=tag['slug']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_tags,
            remove_tags,
        ),
    ]
