import csv

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            with open('../data/ingredients.csv') as f:
                reader = csv.reader(f)
                for row in reader:
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1],
                    )
        except Exception as error:
            raise CommandError("Objects can't to be create", error)
        self.stdout.write(self.style.SUCCESS('Date Base Update.'))
