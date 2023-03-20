from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        'E-mail',
        unique=True,
        help_text='Fill e-mail'
    )

    first_name = models.CharField(
        'First name',
        max_length=150,
        help_text='Fill first name'
    )

    last_name = models.CharField(
        'Last name',
        max_length=150,
        help_text='Fill last name'
    )

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
